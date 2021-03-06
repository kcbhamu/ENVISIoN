#  ENVISIoN
#
#  Copyright (c) 2019 Jesper Ericsson
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##############################################################################################

import sys,os,inspect
# path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# sys.path.insert(0, os.path.expanduser(path_to_current_folder))

import inviwopy
import threading
import numpy as np
from matplotlib import pyplot as plt 
import h5py
from .NetworkHandler import NetworkHandler
from envisionpy.utils.exceptions import *

# TODO: Add support for adding tf points to specific channels if multichannel is activated.
#       Right now all 4 transferfunctions in multichannel raycaster will always be identical. 

class VolumeNetworkHandler(NetworkHandler):
    """ Base class for setting up and handling a self.network for generic volume rendering for ENVISIoN.
    Need to be supplied with outports of volume data from somewhere.
    Do not use directly, inherited in other classes for handling specific visualizations.

    """
    def __init__(self, inviwoApp, isMultichannel=False):
        NetworkHandler.__init__(self, inviwoApp)
        self.isMultichannel = isMultichannel
        self.volumeInports = []
        self.setup_volume_network()

        self.transperancy_before = True

        # Set initial conditions
        self.clear_tf()
        self.toggle_slice_canvas(False)
        self.set_plane_normal()
        self.set_slice_background(inviwopy.glm.vec4(0,0,0,1),
                            inviwopy.glm.vec4(1,1,1,1),3,0)
        self.slice_copy_tf()

        self.add_tf_point(0.45, [0.1, 0.1, 0.8, 0.05])
        self.add_tf_point(0.5, [0.2, 0.8, 0.1, 0.1])
        self.add_tf_point(0.8, [0.9, 0.1, 0.1, 0.5])
        # self.set_mask(self.get_tf_points()[0][0], 1)

    def get_ui_data(self):
        return [
            "volume",
            self.get_processor('Raycaster').lighting.shadingMode.selectedIndex,
            self.get_background_info(),
            self.get_tf_points(),
            self.transperancy_before,
            self.get_slice_active(),
            self.get_plane_active(),
            self.get_plane_height(),
            self.get_texture_wrap_mode(),
            self.get_slice_zoom(),
            self.get_plane_normal(),
        ]


    def show_volume_dist(self):
    # Shows a histogram plot over volume data
        def start_plot():
            path_to_hdf5 = self.hdf5_path
            volume = self.get_processor("HDF5 To Volume")#self.get_processor('HDF5 To Volume')
            with h5py.File(path_to_hdf5,"r") as h5:
                data = h5[volume.volumeSelection.value].value
                result = []
                [ result.extend(el) for el in data[0] ]
                newResult = []
                [ newResult.append((element + abs(min(result)))/(max(result) + abs(min(result)))) \
                for element in result ]
                dataList= np.array(newResult)
                plt.hist(dataList,bins=200, density = True)
                plt.title("Volume density distribution") 
                plt.show()
        th = threading.Thread(target=start_plot)
        th.start()

# ------------------------------------------
# ------- Property control functions -------

    def set_mask(self, maskMin, maskMax):
    # Set the mask of the transfer function
    # Only volume densities between maskMin and maskMax are visible after this
        
        raycaster = self.get_processor('Raycaster')
        volumeSlice = self.get_processor('Volume Slice')
        if not self.isMultichannel:
            raycaster.isotfComposite.transferFunction.setMask(maskMin, maskMax)
        else:
            getattr(raycaster, 'transfer-functions').transferFunction1.setMask(maskMin, maskMax)
            getattr(raycaster, 'transfer-functions').transferFunction2.setMask(maskMin, maskMax)
            getattr(raycaster, 'transfer-functions').transferFunction3.setMask(maskMin, maskMax)
            getattr(raycaster, 'transfer-functions').transferFunction4.setMask(maskMin, maskMax)
        volumeSlice.tfGroup.transferFunction.setMask(maskMin,maskMax)

# ---- Transfer function ----

    # def toggle_tf_editor(self, enable):
    #     raycaster = self.get_processor('Raycaster')
    #     raycaster.isotfComposite.widgets[0].editorWidget.visible = enable


    def toggle_transperancy_before(self, enable):
        self.transperancy_before = enable
        return self.update_transperancy_before()

    def update_transperancy_before(self):
        if self.transperancy_before and len(self.get_tf_points()) > 0:
            lowestVal = self.get_tf_points()[0][0]
        else:
            lowestVal = 0
        self.set_mask(lowestVal, 1)
        return [lowestVal, 1]

    def slice_copy_tf(self):
    # Function for copying the volume transferfunction to the slice transferfunction
    # Adds a white point just before the first one aswell
        volumeSlice = self.get_processor('Volume Slice')
        raycaster = self.get_processor('Raycaster')

        if not self.isMultichannel:
            volumeSlice.tfGroup.transferFunction.value = raycaster.isotfComposite.transferFunction.value
        else:
            volumeSlice.tfGroup.transferFunction.value = getattr(raycaster, 'transfer-functions').transferFunction1.value
        #VolumeSlice.tfGroup.transferFunction.add(0.0, inviwopy.glm.vec4(0.0, 0.0, 0.0, 1.0))
        #VolumeSlice.tfGroup.transferFunction.add(1.0, inviwopy.glm.vec4(1.0, 1.0, 1.0, 1.0))
        tf_points = self.get_tf_points()
        if len(tf_points) > 0 and tf_points[0][0] != 0:
            volumeSlice.tfGroup.transferFunction.add(0.99*tf_points[0][0], inviwopy.glm.vec4(1.0, 1.0, 1.0, 1.0))

    def clear_tf(self):
    # Clears the transfer function of all points
        Raycaster = self.get_processor('Raycaster')
        if not self.isMultichannel:
            Raycaster.isotfComposite.transferFunction.clear()
        else:
            getattr(Raycaster, 'transfer-functions').transferFunction1.clear()
            getattr(Raycaster, 'transfer-functions').transferFunction2.clear()
            getattr(Raycaster, 'transfer-functions').transferFunction3.clear()
            getattr(Raycaster, 'transfer-functions').transferFunction4.clear()
        self.slice_copy_tf()

    def set_tf_points(self, points):
    # Sets all transfer function points from an array of tf poitns.
        raycaster = self.get_processor('Raycaster')
        if not self.isMultichannel:
            tfProperty = raycaster.isotfComposite.transferFunction
        else:
            tfProperty = getattr(raycaster, 'transfer-functions').transferFunction1
        tfProperty.clear()

        for point in points:
            glm_col = inviwopy.glm.vec4(point[1][0], point[1][1], point[1][2], point[1][3])
            tfProperty.add(point[0], glm_col)

        if self.isMultichannel:
            getattr(raycaster, 'transfer-functions').transferFunction2.value = tfProperty.value
            getattr(raycaster, 'transfer-functions').transferFunction3.value = tfProperty.value
            getattr(raycaster, 'transfer-functions').transferFunction4.value = tfProperty.value
        self.slice_copy_tf()
        self.update_transperancy_before()

    def get_tf_points(self):
    # Return a list of all the transferfunction points
        Raycaster = self.get_processor('Raycaster')
        if not self.isMultichannel:
            tf_property = Raycaster.isotfComposite.transferFunction
        else:
            tf_property = getattr(Raycaster, 'transfer-functions').transferFunction1
        point_list = [[x.pos, [x.color[0], x.color[1], x.color[2], x.color[3]]] for x in tf_property.getValues()]
        return point_list
  
    def add_tf_point(self, value, color):
    # Add point to the raycaster transferfunction
    # Color should be an 4-element-array containing RGBA with values in 0-1 interval.
        raycaster = self.get_processor('Raycaster')
        glm_col = inviwopy.glm.vec4(color[0], color[1], color[2], color[3])
        if not self.isMultichannel:
            raycaster.isotfComposite.transferFunction.add(value, glm_col)
        else:
            getattr(raycaster, 'transfer-functions').transferFunction1.add(value, glm_col)
            getattr(raycaster, 'transfer-functions').transferFunction2.add(value, glm_col)
            getattr(raycaster, 'transfer-functions').transferFunction3.add(value, glm_col)
            getattr(raycaster, 'transfer-functions').transferFunction4.add(value, glm_col)
        self.slice_copy_tf()
        self.update_transperancy_before()
            
    # def remove_tf_point(self, index):
    # # Remove a point by index
    #     Raycaster = self.get_processor('Raycaster')
    #     if not self.isMultichannel:
    #         tf_property = Raycaster.isotfComposite.transferFunction
    #         if len(self.get_tf_points()) <= index:
    #             raise EnvisionError("No tf point to remove.")
    #         point_to_remove = tf_property.getValueAt(index)
    #         tf_property.remove(point_to_remove)
    #         self.slice_copy_tf()
    #         self.update_transperancy_before()

    # def set_tf_point_color(self, value, color):
    # # Changes the color of a tf point at a certain value
    #     Raycaster = self.get_processor('Raycaster')
    #     # Remove the point at the specified value
    #     points = Raycaster.isotfComposite.transferFunction.getValues()
    #     for i in range(len(points)):
    #         if points[i].pos == value:
    #             self.remove_tf_point(i)
    #             break
    #     else:
    #         raise EnvisionError("TF point value not found.")
    #     self.add_tf_point(value, color)

    


# ---- Other Properties ----

    def set_shading_mode(self, mode):
        Raycaster = self.get_processor('Raycaster')
        Raycaster.lighting.shadingMode.value = mode

    def set_volume_background(self, color_1 = None, color_2 = None, styleIndex = None, blendModeIndex = None):
    # Set the background of the volume canvas
        Background = self.get_processor("VolumeBackground")
        if styleIndex != None:
            Background.backgroundStyle.selectedIndex = styleIndex
        if color_1 != None:
            glm_col = inviwopy.glm.vec4(color_1[0], color_1[1], color_1[2], color_1[3])
            Background.bgColor1.value = glm_col
        if color_2 != None:
            glm_col = inviwopy.glm.vec4(color_2[0], color_2[1], color_2[2], color_2[3])
            Background.bgColor2.value = glm_col
        if blendModeIndex != None:
            Background.blendMode.selectedIndex = blendModeIndex

    def set_slice_background(self, color_1 = None, color_2 = None, styleIndex = None, blendModeIndex = None):
    # Set the background of the volume canvas
        Background = self.get_processor("SliceBackground")
        if styleIndex != None:
            Background.backgroundStyle.selectedIndex = styleIndex
        if color_1 != None:
            Background.bgColor1.value = color_1
        if color_2 != None:
            Background.bgColor2.value = color_2
        if blendModeIndex != None:
            Background.blendMode.selectedIndex = blendModeIndex

    def toggle_slice_plane(self, enable):
    # Set if the slice plane should be visible in the volume
        Raycaster = self.get_processor('Raycaster')
        Raycaster.positionindicator.enable.value = enable

    def set_plane_normal(self, x=0, y=1, z=0):
    # Set the normal of the slice plane
    # x, y, and z can vary between 0 and 1
    # TODO: move sliceAxis.value to some initialization code
        VolumeSlice = self.get_processor('Volume Slice')
        VolumeSlice.sliceAxis.value = 3
        VolumeSlice.planeNormal.value = inviwopy.glm.vec3(x, y, z)

    def set_plane_height(self, height):
    # Set the height of the volume slice plane
    # Height can vary between 0 and 1.
        VolumeSlice = self.get_processor('Volume Slice')
        VolumeSlice.planePosition.value = inviwopy.glm.vec3(height, height, height)

    def set_texture_wrap_mode(self, mode):
        volumeSlice = self.get_processor('Volume Slice')
        volumeSlice.trafoGroup.volumeWrapping.selectedIndex = mode

    def set_slice_zoom(self, zoom):
        volumeSlice = self.get_processor('Volume Slice')
        volumeSlice.trafoGroup.imageScale.value = zoom

    # def set_camera_fov(self, fov):
    #     self.get_processor("Mesh Renderer").

    def get_slice_active(self):
        try:
            self.get_processor('SliceCanvas')
            return True
        except ProcessorNotFoundError:
            return False

    def get_plane_active(self):
        return self.get_processor('Raycaster').positionindicator.enable.value

    def get_plane_height(self):
        return self.get_processor('Volume Slice').planePosition.value.x

    def get_slice_zoom(self):
        return self.get_processor('Volume Slice').trafoGroup.imageScale.value

    def get_texture_wrap_mode(self):
        return self.get_processor('Volume Slice').trafoGroup.volumeWrapping.selectedIndex

    def get_plane_normal(self):
        vec = self.get_processor('Volume Slice').planeNormal.value
        return [vec.x, vec.y, vec.z]

    def get_background_info(self):
        background = self.get_processor("VolumeBackground")
        style = background.backgroundStyle.selectedIndex
        col_1 = background.bgColor1.value
        col_2 = background.bgColor2.value
        return [
            [col_1.r, col_1.g, col_1.b], 
            [col_2.r, col_2.g, col_2.b], 
            style]
# ------------------------------------------
# ------- Network building functions -------

    def toggle_slice_canvas(self, enable_slice):
    # Will add or remove the slice canvas
        try:
            sliceCanvas = self.get_processor('SliceCanvas')
        except ProcessorNotFoundError:
            sliceCanvas = None
        
        # If already in correct mode dont do anything
        if (sliceCanvas and enable_slice) or (not sliceCanvas and not enable_slice):
            return

        if enable_slice:
            sliceCanvas = self.add_processor('org.inviwo.CanvasGL', 'SliceCanvas', 25*7, 525)
            sliceCanvas.inputSize.dimensions.value = inviwopy.glm.ivec2(500, 500)       
            self.network.addConnection(self.get_processor('SliceBackground').getOutport('outport'), sliceCanvas.getInport('inport'))
        else:
            self.remove_processor('SliceCanvas')

    def connect_volume(self, volume_outport):
        for inport in self.volumeInports:
            self.network.addConnection(volume_outport, inport)

    def setup_volume_network(self):
    # Setup the generic part of volume rendering self.network.
        xpos = 0
        ypos = 0

        # Add "Bounding Box" and "Mesh Renderer" processors to visualise the borders of the volume
        BoundingBox = self.add_processor('org.inviwo.VolumeBoundingBox', 'Volume Bounding Box', xpos+200, ypos+150)    
        MeshRenderer = self.add_processor('org.inviwo.GeometryRenderGL', 'Mesh Renderer', xpos+200, ypos+225)

        # Add processor to pick which part of the volume to render
        CubeProxyGeometry = self.add_processor('org.inviwo.CubeProxyGeometry', 'Cube Proxy Geometry', xpos+30, ypos+150)
        
        # Add processor to control the camera during the visualisation
        EntryExitPoints = self.add_processor('org.inviwo.EntryExitPoints', 'EntryExitPoints', xpos+30, ypos+225)


        if not self.isMultichannel:
            Raycaster = self.add_processor('org.inviwo.VolumeRaycaster', "Raycaster", xpos, ypos+300)
            Raycaster.raycaster.renderingType.selectedIndex = 1
        else:
            Raycaster = self.add_processor('org.inviwo.MultichannelRaycaster', "Raycaster", xpos, ypos+300)
        # Raycaster.isotfComposite.initializeWidget()
        Raycaster.raycaster.samplingRate.value = 4

        # Setup Slice rendering part
        VolumeSlice = self.add_processor('org.inviwo.VolumeSliceGL', 'Volume Slice', xpos-25*7, ypos+300)   
        SliceCanvas = self.add_processor('org.inviwo.CanvasGL', 'SliceCanvas', xpos-25*7, ypos+525)
        SliceCanvas.inputSize.dimensions.value = inviwopy.glm.ivec2(500, 500)       
        SliceBackground = self.add_processor('org.inviwo.Background', 'SliceBackground', xpos-25*7, ypos+450)
        
        # self.network.addConnection(HDFvolume.getOutport('outport'), VolumeSlice.getInport('volume'))
        self.network.addConnection(VolumeSlice.getOutport('outport'), SliceBackground.getInport('inport'))
        self.network.addConnection(SliceBackground.getOutport('outport'), SliceCanvas.getInport('inport'))

        # Setup volume rendering part
        Canvas = self.add_processor('org.inviwo.CanvasGL', 'Canvas', xpos, ypos+525)
        Canvas.inputSize.dimensions.value = inviwopy.glm.ivec2(500, 500)
        VolumeBackground = self.add_processor('org.inviwo.Background', 'VolumeBackground', xpos, ypos+450)
        
        self.network.addConnection(Raycaster.getOutport('outport'), VolumeBackground.getInport('inport'))
        self.network.addConnection(VolumeBackground.getOutport('outport'), Canvas.getInport('inport'))

        self.network.addLink(VolumeSlice.getPropertyByIdentifier('planePosition'), Raycaster.getPropertyByIdentifier('positionindicator').plane1.position)
        self.network.addLink(VolumeSlice.getPropertyByIdentifier('planeNormal'), Raycaster.getPropertyByIdentifier('positionindicator').plane1.normal)

        # Shared connections and properties between electron density and electron localisation function data
        self.network.addConnection(MeshRenderer.getOutport('image'), Raycaster.getInport('bg'))
        self.network.addConnection(EntryExitPoints.getOutport('entry'), Raycaster.getInport('entry'))
        self.network.addConnection(EntryExitPoints.getOutport('exit'), Raycaster.getInport('exit'))
        self.network.addConnection(BoundingBox.getOutport('mesh'), MeshRenderer.getInport('geometry'))
        self.network.addConnection(CubeProxyGeometry.getOutport('proxyGeometry'), EntryExitPoints.getInport('geometry'))
        self.network.addConnection(VolumeBackground.getOutport('outport'), Canvas.getInport('inport'))
        self.network.addLink(MeshRenderer.getPropertyByIdentifier('camera'), EntryExitPoints.getPropertyByIdentifier('camera'))

        self.volumeInports.append(BoundingBox.getInport('volume'))
        self.volumeInports.append(CubeProxyGeometry.getInport('volume'))
        self.volumeInports.append(Raycaster.getInport('volume'))
        self.volumeInports.append(VolumeSlice.getInport('volume'))

        entryExitPoints_lookFrom_property = EntryExitPoints.getPropertyByIdentifier('camera').getPropertyByIdentifier('lookFrom')
        entryExitPoints_lookFrom_property.value = inviwopy.glm.vec3(0,0,8)

        # Setup slice plane
        pos_indicator = Raycaster.positionindicator
        pos_indicator.plane1.enable.value = True
        pos_indicator.plane2.enable.value = False
        pos_indicator.plane3.enable.value = False
        pos_indicator.enable.value = False # Disabled by default
        pos_indicator.plane1.color.value = inviwopy.glm.vec4(1, 1, 1, 0.5)

        # Connect unitcell and volume visualisation.
        try:
            UnitCellRenderer = self.get_processor('Unit Cell Renderer')
        except ProcessorNotFoundError:
            print("No unitcell processor active")
        else:
            self.network.addConnection(UnitCellRenderer.getOutport('image'), MeshRenderer.getInport('imageInport'))
            self.network.addLink(UnitCellRenderer.getPropertyByIdentifier('camera'), MeshRenderer.getPropertyByIdentifier('camera'))
            self.network.addLink(MeshRenderer.getPropertyByIdentifier('camera'), UnitCellRenderer.getPropertyByIdentifier('camera'))
