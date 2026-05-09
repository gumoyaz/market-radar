from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


class KiwoomDependencyError(RuntimeError):
    pass


class KiwoomRuntimeError(RuntimeError):
    pass


@dataclass
class _LiveTick:
    symbol: str
    ts: str
    price: float
    turnover_billion: float
    real_type: str


class KiwoomLiveAdapter:
    """Thin Kiwoom OpenAPI+ bridge with optional debug logging."""

    def __init__(
        self,
        screen_no: str,
        login_timeout_sec: int,
        debug_log_path: str | None = None,
    ) -> None:
        self.screen_no = screen_no
        self.login_timeout_sec = login_timeout_sec
        self._connected = False
        self._ticks: dict[str, _LiveTick] = {}
        self._debug_log_path = Path(debug_log_path) if debug_log_path else None
        self._setup_qax()

    def _setup_qax(self) -> None:
        if self._setup_pyqt():
            self._backend = "pyqt"
            return

        if self._setup_win32com():
            self._backend = "win32com"
            return

        raise KiwoomDependencyError(
            "Kiwoom live mode needs either PyQt5.QAxContainer or pywin32 "
            "(win32com/pythoncom) on a Windows machine with Kiwoom OpenAPI+ installed."
        )

    def _setup_pyqt(self) -> bool:
        try:
            from PyQt5.QtCore import QEventLoop
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QAxContainer import QAxWidget
        except Exception:
            return False

        self._QEventLoop = QEventLoop
        self._app = QApplication.instance() or QApplication([])
        self._control = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        if self._control.isNull():
            raise KiwoomDependencyError(
                "Kiwoom OpenAPI+ ActiveX control was not found. "
                "Install Kiwoom OpenAPI+ on this Windows machine first."
            )

        self._control.OnEventConnect.connect(self._on_event_connect)
        self._control.OnReceiveRealData.connect(self._on_receive_real_data)
        self._ensure_native_handle()
        return True

    def _setup_win32com(self) -> bool:
        try:
            import pythoncom
            import win32com.client
        except Exception:
            return False

        self._pythoncom = pythoncom
        self._pythoncom.CoInitialize()

        adapter = self

        class _KiwoomEventSink:
            def OnEventConnect(self, err_code: int) -> None:  # noqa: N802
                adapter._on_event_connect(err_code)

            def OnReceiveRealData(self, code: str, real_type: str, real_data: str) -> None:  # noqa: N802
                adapter._on_receive_real_data(code, real_type, real_data)

        try:
            self._control = win32com.client.DispatchWithEvents(
                "KHOPENAPI.KHOpenAPICtrl.1",
                _KiwoomEventSink,
            )
        except Exception as exc:
            raise KiwoomDependencyError(
                "win32com could not bind the Kiwoom ActiveX control."
            ) from exc

        self._app = None
        return True

    def connect(self) -> None:
        if getattr(self, "_backend", "") == "pyqt":
            result = self._control.dynamicCall("CommConnect()")
        else:
            result = self._control.CommConnect()
        self._debug(f"comm_connect result={result}")
        if result != 0:
            raise KiwoomRuntimeError(f"CommConnect() failed with code {result}")

        started = time.time()
        while not self._connected:
            if time.time() - started > self.login_timeout_sec:
                raise KiwoomRuntimeError("Timed out waiting for Kiwoom login.")
            self._pump_once()
            time.sleep(0.05)

    def register_symbols(self, symbols: list[str]) -> None:
        if not symbols:
            raise KiwoomRuntimeError("No symbols provided for SetRealReg.")

        fid_list = "10;14;20"
        for index, symbol in enumerate(symbols):
            opt_type = "0" if index == 0 else "1"
            if getattr(self, "_backend", "") == "pyqt":
                result = self._control.dynamicCall(
                    "SetRealReg(QString, QString, QString, QString)",
                    self.screen_no,
                    symbol,
                    fid_list,
                    opt_type,
                )
            else:
                result = self._control.SetRealReg(self.screen_no, symbol, fid_list, opt_type)

            self._debug(
                f"set_real_reg screen={self.screen_no} symbol={symbol} "
                f"fid_list={fid_list} opt_type={opt_type} result={result}"
            )
            if result != 0:
                raise KiwoomRuntimeError(f"SetRealReg() failed for {symbol} with code {result}")

        self._debug(f"connect_state={self.get_connect_state()}")

    def get_connect_state(self) -> int:
        if getattr(self, "_backend", "") == "pyqt":
            state = self._control.dynamicCall("GetConnectState()")
        else:
            state = self._control.GetConnectState()
        return int(state)

    def pump(self, seconds: int) -> None:
        deadline = time.time() + seconds
        while time.time() < deadline:
            self._pump_once()
            time.sleep(0.05)

    def get_symbol_snapshot(self, symbol: str) -> dict[str, str] | None:
        tick = self._ticks.get(symbol)
        if tick is None:
            return None
        return {
            "ts": tick.ts,
            "price": f"{tick.price:.2f}",
            "turnover_billion": f"{tick.turnover_billion:.1f}",
        }

    def close(self) -> None:
        try:
            if getattr(self, "_backend", "") == "pyqt":
                self._control.dynamicCall("DisconnectRealData(QString)", self.screen_no)
            else:
                self._control.DisconnectRealData(self.screen_no)
        except Exception:
            pass
        finally:
            if hasattr(self, "_pythoncom"):
                try:
                    self._pythoncom.CoUninitialize()
                except Exception:
                    pass

    def _on_event_connect(self, err_code: int) -> None:
        self._debug(f"event_connect err_code={err_code}")
        if err_code != 0:
            raise KiwoomRuntimeError(f"OnEventConnect returned error {err_code}")
        self._connected = True

    def _on_receive_real_data(self, code: str, real_type: str, _real_data: str) -> None:
        price_raw = self._get_real_data(code, 10)
        turnover_raw = self._get_real_data(code, 14)
        trade_time_raw = self._get_real_data(code, 20)
        current_volume_raw = self._get_real_data(code, 15)
        best_ask_raw = self._get_real_data(code, 27)
        best_bid_raw = self._get_real_data(code, 28)
        self._debug(
            "real_data "
            f"code={code} real_type={real_type} "
            f"price_raw={price_raw!r} turnover_raw={turnover_raw!r} time_raw={trade_time_raw!r} "
            f"volume_raw={current_volume_raw!r} ask_raw={best_ask_raw!r} bid_raw={best_bid_raw!r}"
        )

        if not trade_time_raw:
            trade_time_raw = datetime.now().strftime("%H%M%S")

        try:
            price = abs(float(price_raw))
        except ValueError:
            self._debug(
                f"skip_tick code={code} real_type={real_type} invalid_price={price_raw!r}"
            )
            return

        try:
            turnover = abs(float(turnover_raw)) / 100000000.0 if turnover_raw else 0.0
        except ValueError:
            turnover = 0.0

        iso_ts = self._to_iso_timestamp(trade_time_raw)
        self._ticks[code] = _LiveTick(
            symbol=code,
            ts=iso_ts,
            price=price,
            turnover_billion=turnover,
            real_type=real_type,
        )
        self._debug(
            f"tick_saved code={code} real_type={real_type} ts={iso_ts} "
            f"price={price} turnover_billion={turnover:.4f}"
        )

    def _get_real_data(self, code: str, fid: int) -> str:
        if getattr(self, "_backend", "") == "pyqt":
            value = self._control.dynamicCall("GetCommRealData(QString, int)", code, fid)
        else:
            value = self._control.GetCommRealData(code, fid)
        return str(value).strip()

    def _pump_once(self) -> None:
        if getattr(self, "_backend", "") == "pyqt":
            self._app.processEvents()
            return
        self._pythoncom.PumpWaitingMessages()

    def _ensure_native_handle(self) -> None:
        if getattr(self, "_backend", "") != "pyqt":
            return

        self._control.setWindowTitle("KiwoomOpenApiHost")
        self._control.resize(1, 1)
        self._control.move(-10000, -10000)
        self._control.showMinimized()
        self._app.processEvents()
        _ = int(self._control.winId())
        self._app.processEvents()

    def _to_iso_timestamp(self, hhmmss: str) -> str:
        hhmmss = hhmmss.zfill(6)
        now = datetime.now()
        return now.replace(
            hour=int(hhmmss[0:2]),
            minute=int(hhmmss[2:4]),
            second=int(hhmmss[4:6]),
            microsecond=0,
        ).isoformat()

    def _debug(self, message: str) -> None:
        if self._debug_log_path is None:
            return
        self._debug_log_path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._debug_log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"[{timestamp}] {message}\n")
