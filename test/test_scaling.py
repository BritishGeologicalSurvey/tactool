from tactool.main import TACtool


def test_toggle_scaling_mode(tactool: TACtool):
    """
    Function to test the functionality of the scaling mode.
    """
    # Check that the SetScaleDialog and the transparent rectangle
    # on the PyQt Graphics Scene do not exist
    assert tactool.window.set_scale_dialog is None
    assert tactool.graphics_scene.scaling_rect is None
    # Check that the main input widgets are enabled
    for widget in tactool.window.main_input_widgets:
        assert widget.isEnabled() is True
    assert tactool.graphics_view.disable_analysis_points is False

    # Start the scaling mode
    tactool.window.toggle_scaling_mode()

    # Check that the SetScaleDialog and the transparent rectangle
    # on the PyQt Graphics Scene exist and are the correct type
    assert tactool.window.set_scale_dialog is not None
    assert tactool.graphics_scene.scaling_rect is not None
    # Check that the main input widgets are disabled
    for widget in tactool.window.main_input_widgets:
        assert widget.isEnabled() is False
    assert tactool.graphics_view.disable_analysis_points is True

    # Set the scale, following the same steps as the user would
    tactool.window.set_scale_dialog.scale_value.setText(str(2.0))
    tactool.window.set_scale_dialog.set_scale()

    # Check that the SetScaleDialog and the transparent rectangle
    # on the PyQt Graphics Scene do not exist
    assert tactool.window.set_scale_dialog is None
    assert tactool.graphics_scene.scaling_rect is None
    # Check that the main input widgets are enabled
    for widget in tactool.window.main_input_widgets:
        assert widget.isEnabled() is True
    assert tactool.graphics_view.disable_analysis_points is False


def test_set_scale(tactool: TACtool):
    """
    Function to test the functionality of setting the scale.
    """
    # Set the scale, following the same steps as the user would
    scale = 2.0
    tactool.window.toggle_scaling_mode()
    tactool.set_scale_dialog.scale_value.setText(str(scale))
    tactool.set_scale_dialog.set_scale()

    # Add some points, these should now have the new scale
    tactool.graphics_view.left_click.emit(101, 101)
    tactool.graphics_view.left_click.emit(202, 202)
    tactool.graphics_view.left_click.emit(303, 303)

    # Iterate through each actual Analysis Point
    for analysis_point in tactool.table_model.analysis_points:
        # Check that the scale value is equal to expected
        assert analysis_point.scale == scale


def test_scale_hint(tactool: TACtool):
    """
    Function to test the functionality of the Set Scale reminder in the Status Bar.
    """
    # Check Set Scale hint is not visible
    set_scale_status = tactool.window.status_bar_messages["set_scale"]["status"]
    assert set_scale_status is None
    assert set_scale_status not in tactool.window.status_bar.children()

    # Add some points by clicking
    tactool.graphics_view.left_click.emit(101, 101)
    tactool.graphics_view.left_click.emit(202, 202)
    tactool.graphics_view.left_click.emit(303, 303)

    # Check Set Scale hint is visible
    set_scale_status = tactool.window.status_bar_messages["set_scale"]["status"]
    assert set_scale_status is not None
    assert set_scale_status in tactool.window.status_bar.children()

    # Set the scale, following the same steps as the user would
    tactool.window.toggle_scaling_mode()
    tactool.set_scale_dialog.scale_value.setText(str(2.0))
    tactool.set_scale_dialog.set_scale()

    # Check Set Scale hint is not visible
    set_scale_status = tactool.window.status_bar_messages["set_scale"]["status"]
    assert set_scale_status is None
    assert set_scale_status not in tactool.window.status_bar.children()

    # Reset the Scale value to the default value
    tactool.window.reset_settings()

    # Check Set Scale hint is visible
    set_scale_status = tactool.window.status_bar_messages["set_scale"]["status"]
    assert set_scale_status is not None
    assert set_scale_status in tactool.window.status_bar.children()