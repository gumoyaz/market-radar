from __future__ import annotations

import sys


def main() -> None:
    try:
        from PyQt5.QtCore import QTimer
        from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
        from PyQt5.QAxContainer import QAxWidget
    except Exception as exc:
        raise SystemExit(f"PyQt5/QAxContainer import failed: {exc}")

    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Kiwoom Login Host")
    window.resize(420, 120)

    layout = QVBoxLayout(window)
    status = QLabel("Launching Kiwoom login flow. Complete login within 5 minutes.")
    layout.addWidget(status)

    api = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1", window)
    layout.addWidget(api)

    if api.isNull():
        raise SystemExit("Kiwoom ActiveX control could not be created.")

    def on_event_connect(err_code: int) -> None:
        if err_code == 0:
            print("Login successful.")
            status.setText("Login successful.")
            QTimer.singleShot(1000, app.quit)
        else:
            print(f"Login failed with err_code={err_code}")
            status.setText(f"Login failed: err_code={err_code}")
            QTimer.singleShot(1000, app.quit)

    api.OnEventConnect.connect(on_event_connect)

    window.show()
    window.activateWindow()
    window.raise_()
    app.processEvents()

    host_win_id = int(api.winId())
    print(f"Host winId={host_win_id}")
    print("Launching Kiwoom login flow...")
    print("Please complete the Kiwoom login within 5 minutes.")

    result = api.dynamicCall("CommConnect()")
    if result != 0:
        raise SystemExit(f"CommConnect failed with code {result}")

    QTimer.singleShot(300000, lambda: (_print_timeout(status), app.quit()))
    sys.exit(app.exec_())


def _print_timeout(status: "QLabel") -> None:
    print("Timed out waiting for Kiwoom login.")
    status.setText("Timed out waiting for Kiwoom login.")


if __name__ == "__main__":
    main()
