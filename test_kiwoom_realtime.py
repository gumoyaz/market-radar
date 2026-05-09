from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path


def _log(message: str, logfile: Path) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    logfile.parent.mkdir(parents=True, exist_ok=True)
    with logfile.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def main() -> None:
    try:
        from PyQt5.QtCore import QTimer
        from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
        from PyQt5.QAxContainer import QAxWidget
    except Exception as exc:
        raise SystemExit(f"PyQt5/QAxContainer import failed: {exc}")

    symbol = "005930"
    screen_no = "9998"
    logfile = Path("logs/kiwoom_realtime_stdout.log")
    if logfile.exists():
        logfile.unlink()

    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Kiwoom Realtime Debug")
    window.resize(460, 160)

    layout = QVBoxLayout(window)
    status = QLabel("Waiting for login...")
    layout.addWidget(status)

    api = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1", window)
    layout.addWidget(api)

    if api.isNull():
        raise SystemExit("Kiwoom ActiveX control could not be created.")

    def get_real(fid: int) -> str:
        return str(api.dynamicCall("GetCommRealData(QString, int)", symbol, fid)).strip()

    def on_receive_real_data(code: str, real_type: str, _real_data: str) -> None:
        price = get_real(10)
        turnover = get_real(14)
        trade_time = get_real(20)
        volume = get_real(15)
        _log(
            f"real_data code={code} real_type={real_type} "
            f"price={price!r} turnover={turnover!r} time={trade_time!r} volume={volume!r}",
            logfile,
        )

    def on_event_connect(err_code: int) -> None:
        _log(f"event_connect err_code={err_code}", logfile)
        if err_code != 0:
            status.setText(f"Login failed: {err_code}")
            return

        status.setText(f"Logged in. Registering {symbol}...")
        state = api.dynamicCall("GetConnectState()")
        _log(f"connect_state={state}", logfile)
        result = api.dynamicCall(
            "SetRealReg(QString, QString, QString, QString)",
            screen_no,
            symbol,
            "10;14;15;20",
            "0",
        )
        _log(f"set_real_reg symbol={symbol} result={result}", logfile)
        status.setText(f"Registered {symbol}. Waiting for realtime events...")

    api.OnEventConnect.connect(on_event_connect)
    api.OnReceiveRealData.connect(on_receive_real_data)

    window.show()
    window.activateWindow()
    window.raise_()
    app.processEvents()

    _log(f"host_winid={int(api.winId())}", logfile)
    result = api.dynamicCall("CommConnect()")
    _log(f"comm_connect result={result}", logfile)
    if result != 0:
        raise SystemExit(f"CommConnect failed with code {result}")

    QTimer.singleShot(300000, lambda: (_log("timeout", logfile), app.quit()))
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
