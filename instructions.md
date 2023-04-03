## Tool Bar - File

To access file functionality, press the _File_ button in the toolbar, located at the top left of the application.

### Import Image

_Import an image into the application._

- Press the _Import Image_ button.
- Select a image file using the file picker.

### Export Image

_Export the current image with the current analysis points added to it._

- Press the _Export Image_ button.
- Locate the directory you wish to export the image file to.
- Input the filename for the image file.

By default, the exported file will be a PNG file. However, you can add your own file extension to the filename if you wish to create a different file type.

### Import TACtool CSV

_Import a CSV file of previously exported TACtool analysis point data._

- Press the _Import TACtool CSV_ button.
- Select a CSV file using the file picker.

The selected CSV must be a file of previously saved coordinates, i.e. a TACtool CSV format.

### Export TACtool CSV

_Export the current analysis point data to a TACtool CSV file._

- Press the _Export TACtool CSV_ button.
- Locate the directory you wish to export the CSV file to.
- Input the filename for the CSV file.

By default, the exported file will be a CSV file. However, you can add your own file extension to the filename if you wish to create a different file type, though this is not recommended.

## User Interface Buttons

### Clear Points

_Clear all of the currently existing analysis points._

### Reset IDs

_Reset the ID values of the currently existing analysis points. This will make the ID values increment sequentially, starting from 1._

### Reset Settings

_Reset the current analysis point settings to default._
- _sample_name = None_
- _mount_name = None_
- _material = None_
- _colour = yellow/#ffff00_
- _diameter = 10_
- _scale = 1.0_

## Analysis Point Settings

Analysis point settings should be selected before an analysis point is created.

### Metadata Fields

To change a metadata field value, _Left Click_ twice on the cell containing the value you would like to modify. Once you have inputted your new value, press _Enter_ to confirm the change.

### Label

To change the label, click on the drop-down menu next to _Label_ and select your label. A label can be either "RefMark" or "Spot".

_A label value can be changed after analysis point creation. Simply Left Click twice on the cell containing the value you would like to modify. Once you have inputted your new value, press Enter to confirm the change._

### Colour

To change the colour, click on the colour box next to _Colour_ and use the colour picker to select a colour.

### Diameter

To change the diameter, either use the up/down arrows next to the _Diameter_ input box, or type in your own value. It must be a whole number.

_Note: The **Diameter** is measured in **µm**_

### Scale

The scale can be set in 1 of 2 ways.

**Set Scale Dialog**

- Press the _Set Scale_ button. A _Set Scale_ window will then open.
- The image on the main window will become slightly grey. This means you can now draw a line across the image. Start by clicking once to create the start of the line and clicking again to create the end of the line. Pressing the _Clear_ button will remove any current lines.
- Now you change the estimated distance in microns. To do this, either use the up/down arrows next to the _Distance_ input box, or type in your own value. It must be a whole number.
- Pressing _OK_ will confirm the new scale and close the _Set Scale_ window.

**Directly Setting the Scale Value**

Alternatively, if you already know the scale value you would like to use, you can input this by typing it into the _Scale_ input box on the main window, next to the _Set Scale_ button.

_Note: The **Scale** is measured in **Pixels per µm**_

## Analysis Points

### Creating Analysis Points

With your analysis point settings already defined, you can _Left Click_ anywhere on the currently loaded image to place an analysis point at that location.
Analysis points will be displayed in your selected colour, along with their assigned ID value and selected label.

### Removing Analysis Points

You can _Right Click_ anywhere within an existing analysis point circle to remove the analysis point. If you have multiple analysis point stacked on top of one another, the last analysis point placed will be the analysis point at the top of the stack. Therefore, when using _Right Click_ on a stack of analysis point, the analysis point at the top of the stack will be removed first.

### Modifying Analysis Points Settings

You can _Left Click_ on the _id_ value of an existing analysis point within the table data. Doing so will set all analysis point settings to the be the same as the settings of the selected and existing analysis point.

## Analysis Points Table Data

### Displayed Data

Data which is displayed within the table at the bottom of the window displays the list of analysis point currently on the image. This data includes the following:
- id _(The ID value assigned to the analysis point. This is automatically incremented when new analysis points are added.)_
- label _(The label assigned to the analysis point. Either "RefMark" or "Spot".)_
- x _(The x coordinate location of the analysis point on the image.)_
- y _(The y coordinate location of the analysis point on the image.)_
- diameter _(The diameter of the analysis point measured in **µm**.)_
- scale _(The scale of the analysis point measured in **Pixels per µm**.)_
- colour _(The colour of the analysis point, represented in a Hex Colour Code.)_
- sample_name _(The sample name assigned to the analysis point.)_
- mount_name _(The mount name assigned to the analysis point.)_
- material _(The material assigned to the analysis point)_
- notes _(Any notes assigned to the analysis point.)_

The following fields can be modified after placing an analysis point. To modify these values, _Left Click_ twice on the cell containing the value you would like to modify. Once you have inputted your new value, press _Enter_ to confirm the change.
- _label_
- _sample_name_
- _mount_name_
- _material_
- _notes_

## Image Navigation

To avoid issues image navigation issues, it is recommended to tab into the image viewer before attempting to navigate it. To do this, simply place your mouse over the current image, and press the _Middle Mouse Button_.

To enable Image Navigation, hold down the _Ctrl_ key.
Image Navigation mode will be automatically disabled when you stop holding the _Ctrl_ key.

### Zooming

Whilst Image Navigation is enabled, simply use the mouse scroll wheel. Scrolling _down_ will zoom out, whilst scrolling _up_ will zoom in.

### Panning

Whilst Image Navigation is enabled, hold down _Left Click_ on the current image and move your mouse to pan the image.

**OR**

You can use the arrow keys to move across the image in the corresponding direction.
