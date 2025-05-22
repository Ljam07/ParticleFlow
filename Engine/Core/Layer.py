class Layer:
    """
    Base class for all layers in the application.
    """
    def __init__(self, name="Layer"):
        self.name = name
        self.attached = False

    def OnAttach(self):
        """Called once when the layer is added to the stack."""
        # Override in subclass if needed
        print("Attached layer")
        pass
    
    def OnDetach(self):
        """Called once when the layer is removed from the stack."""
        # Override in subclass if needed
        pass

    def OnUpdate(self, dt):
        """Called every frame to update the layer logic."""
        # Override in subclass if needed
        pass

    def OnEvent(self, event):
        """Called when an input or window event occurs. Return True if handled."""
        # Override in subclass if needed
        return False

    def OnUI(self):
        """Called every frame to render UI."""
        # Override in subclass if needed
        pass

class LayerStack:
    """
    Manages a list of layers, calling their lifecycle methods in order.
    """
    def __init__(self):
        self._layers = []  # list of Layer instances

    def PushLayer(self, layer):
        """Add a layer and call its attach hook."""
        self._layers.append(layer)
        layer.attached = True
        layer.OnAttach()

    def PopLayer(self, layer):
        """Remove a layer and call its detach hook."""
        if layer in self._layers:
            self._layers.remove(layer)
            layer.OnDetach()
            layer.attached = False

    def OnUpdate(self, dt):
        """Call on_update for each layer in insertion order."""
        for layer in self._layers:
            layer.OnUpdate(dt)

    def OnEvent(self, event):
        """Dispatch an event to layers in reverse order until handled."""
        for layer in reversed(self._layers):
            handled = layer.OnEvent(event)
            if handled:
                break

    def OnUI(self):
        """Call on_ui for each layer."""
        for layer in self._layers:
            layer.OnUI()
