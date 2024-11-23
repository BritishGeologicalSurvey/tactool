## Analysis Points

### Creating Analysis Points

With your analysis point settings already defined, you can `Left Click` anywhere on the currently loaded image to place an analysis point at that location.
Analysis points will be displayed in your selected `colour`, along with their assigned `id` value and selected `label`.

### Removing Analysis Points

You can `Right Click` anywhere within an existing analysis point circle to remove the analysis point. If you have multiple analysis point stacked on top of one another, the last analysis point placed will be the analysis point at the top of the stack. Therefore, when using `Right Click` on a stack of analysis point, the analysis point at the top of the stack will be removed first.

### Modifying Analysis Points Settings

You can `Left Click` on the `id` value of an existing analysis point within the table data. Doing so will set all analysis point settings to the be the same as the settings of the selected and existing analysis point.

## Analysis Points Table Data

### Displayed Data

Data which is displayed within the table at the bottom of the window displays the list of analysis point currently on the image. This data includes the following:
- `id`
    - The id value assigned to the analysis point. This is automatically incremented when new analysis points are added.
- `label`
    - The label assigned to the analysis point. Either `RefMark` or `Spot`.
- `x`
    - The x coordinate location of the analysis point on the image.
- `y`
    - The y coordinate location of the analysis point on the image.
- `diameter`
    - The diameter of the analysis point measured in `µm`.
- `scale`
    - The scale of the analysis point measured in `Pixels per µm`.
- `colour`
    - The colour of the analysis point, represented in a Hex Colour Code.
- `sample_name`
    - The sample name assigned to the analysis point.
- `mount_name`
    - The mount name assigned to the analysis point.
- `material`
    - The material assigned to the analysis point.
- `notes`
    - Any notes assigned to the analysis point.

The following fields can be modified after placing an analysis point. To modify these values, `Left Click` twice on the cell containing the value you would like to modify. Once you have inputted your new value, press `Enter` to confirm the change.
- `label`
- `sample_name`
- `mount_name`
- `material`
- `notes`

## Analysis Point Metadata and Settings

When creating a new analysis point, any current metadata field values and analysis point settings will be applied to that new analysis point. Therefore, analysis point metadata fields and settings should be selected before an analysis point is created.

### Metadata Fields

To change a metadata field, `Left Click` on the input box of the metadata field you would like to change and type in your value.

### Label

To change the `label`, click on the drop-down menu next to `Label` and select your label. A `label` can be either `RefMark` or `Spot`.

_Note: A `label` value can be changed after analysis point creation. Simply `Left Click` twice on the cell containing the value you would like to modify. Once you have inputted your new value, press `Enter` to confirm the change._

### Colour

To change the `colour`, click on the colour box next to `Colour` and use the colour picker to select a colour.

### Diameter

To change the `diameter`, either use the up/down arrows next to the `Diameter` input box, or type in your own value. It must be a whole number.

_Note: The `Diameter` is measured in `µm`_

### Scale

To set the scale, complete the following steps:

- Press the `Set Scale` button. A _Set Scale_ window will then open.
- The image on the main window will become slightly grey. This means you can now draw a line across the image. Start by clicking once to create the start of the line and clicking again to create the end of the line. Pressing the `Clear` button will remove any current lines.
- Now you can change the estimated distance in microns. To do this, either use the up/down arrows next to the `Distance` input box, or type in your own value. It must be a whole number.
- Pressing `OK` will confirm the new `scale` and close the _Set Scale_ window.

_Note: The `Scale` is measured in `Pixels per µm`_

## Image Navigation

To avoid issues image navigation issues, it is recommended to tab into the image viewer before attempting to navigate it. To do this, simply place your mouse over the current image, and press the `Middle Mouse Button`.

To enable Image Navigation, hold down the `Ctrl` key.
Image Navigation mode will be automatically disabled when you stop holding the `Ctrl` key.

### Zooming

Whilst Image Navigation is enabled, simply use the mouse scroll wheel. Scrolling `down` will zoom out, whilst scrolling `up` will zoom in.

### Panning

Whilst Image Navigation is enabled, hold down `Left Click` on the current image and move your mouse to pan the image.

**OR**

You can use the arrow keys to move across the image in the corresponding direction.

## User Interface Buttons

### Clear Points

_Clear all of the currently existing analysis points._

### Reset IDs

_Reset the `id` values of the currently existing analysis points. This will make the `id` values increment sequentially, starting from `1`._

### Reset Settings

_Reset the current analysis point settings to default._
- `sample_name` = `None`
- `mount_name` = `None`
- `material` = `None`
- `colour` = `yellow`/`#ffff00`
- `diameter` = `10`
- `scale` = `1.0`

## Toolbar - File

To access file functionality, press the `File` button in the toolbar, located at the top left of the application.

### Import Image

_Import an image into the application._

- Press the `Import Image` button.
- Select an image file using the file picker.

### Export Image

_Export the current image with the current analysis points added to it._

- Press the `Export Image` button.
- Locate the directory you wish to export the image file to.
- Input the filename for the image file.

By default, the exported file will be a `PNG` file. However, you can add your own file extension to the filename if you wish to create a different file type.

### Import TACtool CSV

_Import a `CSV` file of previously exported TACtool analysis point data._

- Press the `Import TACtool CSV` button.
- Select a `CSV` file using the file picker.

The selected `CSV` must be a file of previously saved coordinates, i.e. a TACtool CSV format.

### Export TACtool CSV

_Export the current analysis point data to a TACtool CSV file._

- Press the `Export TACtool CSV` button.
- Locate the directory you wish to export the `CSV` file to.
- Input the filename for the `CSV` file.

By default, the exported file will be a `CSV` file. However, you can add your own file extension to the filename if you wish to create a different file type, though this is not recommended.

_Note: Upon export, the `sample_name` and `id` columns will be concatenated into a single column labelled `Name`, using the character pattern `_#` to join them._

### Import and Recoordinate SEM CSV

_Import and recoordinate a given SEM CSV file, using the current reference points in TACtool._

- Ensure you currently have 3 analysis points with the label `RefMark` placed in TACtool.
- Press the `Import and Recoordinate SEM CSV` button.
- Select an input `CSV` file by clicking on the `Select Input CSV` button and then use the file picker.
- Press the `Import and Recoordinate` button.
- The SEM points from the given CSV file will then be imported as Analysis Points and recoordinated based on the initially placed reference points.

_Notes:_
- _Imported SEM points will retain their existing `Particle ID` values, as they will be used to assign the Analysis Point `id` values._
- _When SEM points are imported from a CSV file, it is assumed that the origin for their coordinates will be **top right**, but the origin in TACtool is **top left**. To account for this, `SEM` coordinates automatically have their `x` axis inverted according to the currently loaded image, thus making their effective origin **top left**._
- _When the SEM points are imported using this method, they will adopt any of the current Analysis Point settings applied in the TACtool window._
- _If there are more than `3` analysis points with the label `RefMark` in TACtool, the recoordination process will only use the first `3` reference points from the Analysis Points Table Data._
