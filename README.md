# TACtool

> A graphical tool for selecting points for analysis on an SEM image

### To use on Windows:

- Download latest Windows build by clicking [here](https://github.com/BritishGeologicalSurvey/tactool/releases/latest/download/TACtool.exe).
- Double click to run. On first run it takes a while to load.


## Class Relationship Diagram

<details>
    <summary>Mermaid JS Code</summary>

    classDiagram
        direction LR

        class TACtool{
            QApplication
            Manages preloaded modes of the application
            ---
            +Window
            +developer_mode: bool
            +testing_mode: bool

            developer_mode()
        }

        class Window {
            QMainWindow
            User Interface with data preprocessing and data flow
            ---
            +testing_mode: bool
            +default_settings: dict
            +image_filepath: str
            +csv_filepath: str
            +point_colour: str
            +status_bar_messages: dict
            +graphics_view: GraphicsView
            +graphics_scene: GraphicsScene
            +table_model: TableModel
            +table_view: TableView
            +set_scale_dialog: SetScaleDialog

            +setup_ui_elements()
            +set_colour_button_style()
            +connect_signals_and_slots()
            +create_status_bar_messages()
            +toggle_status_bar_messages()
            +import_image_get_path()
            +export_image_get_path()
            +import_tactool_csv_get_path()
            +load_tactool_csv_data(filepath)
            +process_tactool_csv(filepath)
            +parse_row_data(item, default_values)
            +export_tactool_csv_get_path()
            +validate_current_data(validate_image)
            +add_analysis_point(x, y, label, diameter, scale, colour, notes, apid, sample_name, mount_name, material, from_click)
            +remove_analysis_point(x, y, apid)
            +reload_analysis_points()
            +reset_analysis_points()
            +clear_analysis_points()
            +update_analysis_points()
            +set_point_colour()
            +toggle_scaling_mode()
            +clear_scale_clicked()
            +set_scale(scale)
            +get_point_settings(analysis_point, clicked_column_index)
            +reset_settings()
            +update_point_settings(sample_name, mount_name, material, label, diameter, scale, colour)
            +data_error_message(error)
            +show_message(title, message, type)
            +closeEvent(event)
        }

        class TableView{
            QTableView
            Manage the display of TableModel data
            ---
            +set_column_sizes()
            +mousePressEvent(event)
            +signal: selected_analysis_point(analysis_point, column)
        }

        class GraphicsView{
            QGraphicsView
            Manage user interaction and visual display of GraphicsScene
            ---
            +_zoom: int
            +_empty: bool
            +_image: QGraphicsPixmapItem
            +navigation_mode: bool
            +set_scale_mode: bool
            +scale_start_point: QPointF
            +scale_end_point: QPointF
            +graphics_scene: GraphicsScene

            +mousePressEvent(event)
            +mouseMoveEvent(event)
            +wheelEvent(event)
            +keyPressEvent(event)
            +keyReleaseEvent(event)
            +configure_frame()
            +load_image(filepath)
            +save_image(filepath)
            +show_entire_image()
            +toggle_scaling_mode()
            +reset_scale_line_points()
            +signal: left_click(x, y)
            +signal: right_click(x, y)
            +signal: scale_move_event(pixel_distance)
        }

        class SetScaleDialog{
            QDialog
            Allows the user to interactively calculate a scale
            ---
            +testing_mode: bool
            +pixel_input_default: str

            +setup_ui_elements()
            +connect_signals_and_slots()
            +update_scale()
            +scale_move_event_handler(pixel_distance)
            +set_scale()
            +closeEvent(event)
            signal: clear_scale()
            signal: set_scale_clicked(scale)
            signal: closed_set_scale_dialog()
        }

        class GraphicsScene{
            QGraphicsScene
            Manage items painted on image
            ---
            +_maximum_point_id: int
            +scaling_rect: QGraphicsRectItem
            +scaling_group: QGraphicsItemGroup
            +scaling_line: QGraphicsLineItem
            +table_model: TableModel

            +add_analysis_point(x, y, label, diameter, scale, colour, notes, apid, sample_name, mount_name, material)
            +remove_analysis_point(x, y, apid)
            +get_ellipse_at(x, y)
            +next_point_id()
            +toggle_transparent_window(graphics_view_image)
            +draw_scale_line(start_point, end_point)
            +draw_scale_point(x, y)
            +remove_scale_items()
        }

        class TableModel{
            QAbstractTableModel
            Manage AnalysisPoint data
            ---
            +headers: list
            +_data: list
            +editable_columns: list

            +headerData(section, orientation, role)
            +columnCount(*args)
            +rowCount(*args)
            +data(index, role)
            +setData(index, value, role)
            +flags(index)
            +add_point(analysis_point)      
            +remove_point(target_id)
            +get_point_by_ellipse(target_ellipse)
            +get_point_by_apid(target_id)
            +reference_points()
            +analysis_points()
            +export_csv(filepath)
            +convert_export_headers()
            +convert_export_point()
            signal: invalid_label_entry(title, message, type)
            signal: updated_analysis_point(index)
        }

        class AnalysisPoint{
            Create AnalysisPoint data
            ---
            +id: int
            +x: int
            +y: int
            +label: str
            +diameter: int
            +scale: float
            +colour: str
            +sample_name: str
            +mount_name: str
            +material: str
            +notes: str
            +_outer_ellipse: QGraphicsEllipseItem
            +_inner_ellipse: QGraphicsEllipseItem
            +_label_text_item: QGraphicsTextItem

            +field_names()
            +aslist()
        }

        TACtool *-- Window
        Window *-- GraphicsView
        Window *-- TableView
        Window *-- SetScaleDialog
        GraphicsView *-- GraphicsScene
        GraphicsScene *-- TableModel
        TableModel *-- AnalysisPoint

        Window <.. TableView : selected_analysis_point(analysis_point, column)
        Window <.. SetScaleDialog : clear_scale()
        Window <.. SetScaleDialog : set_scale_clicked(scale)
        Window <.. SetScaleDialog : closed_set_scale_dialog()
        Window <.. GraphicsView : left_click(x, y)
        Window <.. GraphicsView : right_click(x, y)
        Window <.. GraphicsView : scale_move_event(pixel_distance)

</details>

![TACtool - Class Relationship Diagram](class_relationship_diagram.png)

## Installation

Check out the repository and install dependencies

```bash
pip install -r requirements.txt
```

Run the tool with:

```bash
export PYTHONPATH=.
python tactool/main.py --dev
```

The `--dev` flag starts the application in developer mode, with a test image
pre-loaded into the GraphicsView.

## Running tests

Run the tests with:

```bash
export PYTHONPATH=.
pytest -vv test/
```

### List of Tests

**test_integration.py**
- test_add_and_remove_points
- test_clear_points
- test_reset_id_values
- test_reset_settings
- test_toggle_scaling_mode
- test_set_scale
- test_export_image
- test_import_tactool_csv
- test_export_tactool_csv
- test_reference_point_hint
- test_scale_hint

**test_model.py**
- test_analysis_point_public_attributes_match
- test_model

## Create a standalone executable using PyInstaller

```
pyinstaller --name="TACtool" --windowed --paths=. --onefile tactool/main.py
```
Run the above code and a .spec file and dist/ build/ directories will be created.
