; Открывает окно для кликов в указанных координатах
Func ClickInWindow($windowTitle, $x, $y)
    Local $hWnd = WinGetHandle($windowTitle)
    If @error Then
        ConsoleWrite("Window not found!" & @CRLF)
        Return
    EndIf

    WinActivate($hWnd)
    MouseClick("left", $x, $y)
EndFunc
