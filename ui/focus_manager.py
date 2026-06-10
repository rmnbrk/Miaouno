class UIFocusManager:
    focused_input = None

    @staticmethod
    def set(component):
        UIFocusManager.focused_input = component

    @staticmethod
    def clear():
        UIFocusManager.focused_input = None

    @staticmethod
    def is_focused(component) -> bool:
        return UIFocusManager.focused_input is component