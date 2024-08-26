from __future__ import annotations
import numpy
import typing
__all__ = ['ArducamCamera', 'ArducamFormat', 'ArducamFrame', 'ArducamInfo', 'DepthData', 'RawData', 'TOFConnect', 'TOFControl', 'TOFDeviceType', 'TOFErrorCode', 'TOFOutput', 'TofFrameWorkMode', 'TofWorkMode']
class ArducamCamera:
    def __init__(self) -> None:
        ...
    def close(self) -> TOFErrorCode:
        """
        Close the camera
        """
    def getCameraInfo(self) -> ArducamInfo:
        """
        Get camera information.
        """
    def getControl(self, ctrl: TOFControl) -> int:
        """
        Get camera parameters.
        """
    def open(self, mode: TOFConnect, index: int = 0) -> TOFErrorCode:
        """
        Initialize the camera configuration and turn on the camera, set the initialization frame according to the mode.
        
        - mode Specify the connection method.
        - index Device node, the default value is video0.
        """
    def openWithFile(self, path: str, index: int = 0) -> TOFErrorCode:
        """
        Initialize the camera configuration and turn on the camera, set the initialization frame according to the mode.
        
        - path Specify the config file path.
        - index Device node, the default value is video0.
        """
    def releaseFrame(self, frame: ArducamFrame) -> TOFErrorCode:
        """
        Free the memory space of the frame.
        """
    def requestFrame(self, timeout: int) -> ArducamFrame:
        """
        Request a frame of data from the frame processing thread.
        """
    def setControl(self, ctrl: TOFControl, value: int) -> TOFErrorCode:
        """
        Set camera parameters.
        """
    def start(self, type: TOFOutput) -> TOFErrorCode:
        """
        Start the camera stream and start processing.
        """
    def stop(self) -> TOFErrorCode:
        """
        Stop camera stream and processing.
        """
class ArducamFormat:
    height: int
    timestamp: int
    type: TOFOutput
    width: int
class ArducamFrame:
    pass
class ArducamInfo:
    bit_width: int
    bpp: int
    connect: TOFConnect
    device_type: TOFDeviceType
    height: int
    index: int
    type: TOFOutput
    width: int
class DepthData(ArducamFrame):
    def getAmplitudeData(self) -> numpy.ndarray[typing.Any, numpy.dtype[numpy.float32]]:
        """
        Get amplitude data from the frame
        """
    def getConfidenceData(self) -> numpy.ndarray[typing.Any, numpy.dtype[numpy.float32]]:
        """
        Get confidence data from the frame
        """
    def getDepthData(self) -> numpy.ndarray[typing.Any, numpy.dtype[numpy.float32]]:
        """
        Get depth data from the frame
        """
    def getFrameFormat(self) -> ArducamFormat:
        """
        Get the information of this frame
        """
class RawData(ArducamFrame):
    def getFrameFormat(self) -> ArducamFormat:
        """
        Get the information of this frame
        """
    def getRawData(self: ArducamFrame) -> numpy.ndarray[typing.Any, numpy.dtype[numpy.int16]]:
        """
        Get raw data from the frame
        """
class TOFConnect:
    """
    Members:
    
      CSI
    
      USB
    """
    CSI: typing.ClassVar[TOFConnect]  # value = <TOFConnect.CSI: 0>
    USB: typing.ClassVar[TOFConnect]  # value = <TOFConnect.USB: 1>
    __members__: typing.ClassVar[dict[str, TOFConnect]]  # value = {'CSI': <TOFConnect.CSI: 0>, 'USB': <TOFConnect.USB: 1>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class TOFControl:
    """
    Members:
    
      RANGE
    
      FMT_WIDTH
    
      FMT_HEIGHT
    
      MODE
    
      FRAME_MODE
    
      EXPOSURE
    
      FRAME_RATE
    
      SKIP_FRAME
    
      SKIP_FRAME_LOOP
    
      CONFIG_DIR_EXT
    """
    CONFIG_DIR_EXT: typing.ClassVar[TOFControl]  # value = <TOFControl.CONFIG_DIR_EXT: 256>
    EXPOSURE: typing.ClassVar[TOFControl]  # value = <TOFControl.EXPOSURE: 5>
    FMT_HEIGHT: typing.ClassVar[TOFControl]  # value = <TOFControl.FMT_HEIGHT: 2>
    FMT_WIDTH: typing.ClassVar[TOFControl]  # value = <TOFControl.FMT_WIDTH: 1>
    FRAME_MODE: typing.ClassVar[TOFControl]  # value = <TOFControl.FRAME_MODE: 4>
    FRAME_RATE: typing.ClassVar[TOFControl]  # value = <TOFControl.FRAME_RATE: 6>
    MODE: typing.ClassVar[TOFControl]  # value = <TOFControl.MODE: 3>
    RANGE: typing.ClassVar[TOFControl]  # value = <TOFControl.RANGE: 0>
    SKIP_FRAME: typing.ClassVar[TOFControl]  # value = <TOFControl.SKIP_FRAME: 7>
    SKIP_FRAME_LOOP: typing.ClassVar[TOFControl]  # value = <TOFControl.SKIP_FRAME_LOOP: 8>
    __members__: typing.ClassVar[dict[str, TOFControl]]  # value = {'RANGE': <TOFControl.RANGE: 0>, 'FMT_WIDTH': <TOFControl.FMT_WIDTH: 1>, 'FMT_HEIGHT': <TOFControl.FMT_HEIGHT: 2>, 'MODE': <TOFControl.MODE: 3>, 'FRAME_MODE': <TOFControl.FRAME_MODE: 4>, 'EXPOSURE': <TOFControl.EXPOSURE: 5>, 'FRAME_RATE': <TOFControl.FRAME_RATE: 6>, 'SKIP_FRAME': <TOFControl.SKIP_FRAME: 7>, 'SKIP_FRAME_LOOP': <TOFControl.SKIP_FRAME_LOOP: 8>, 'CONFIG_DIR_EXT': <TOFControl.CONFIG_DIR_EXT: 256>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class TOFDeviceType:
    """
    Members:
    
      VGA
    
      HQVGA
    """
    HQVGA: typing.ClassVar[TOFDeviceType]  # value = <TOFDeviceType.HQVGA: 1>
    VGA: typing.ClassVar[TOFDeviceType]  # value = <TOFDeviceType.VGA: 0>
    __members__: typing.ClassVar[dict[str, TOFDeviceType]]  # value = {'VGA': <TOFDeviceType.VGA: 0>, 'HQVGA': <TOFDeviceType.HQVGA: 1>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class TOFErrorCode:
    """
    Members:
    
      ArducamSuccess
    
      ArducamInvalidParameter
    
      ArducamNoCache
    
      ArducamUnkownDevice
    
      ArducamNotImplemented
    
      ArducamSkipFrame
    
      ArducamSystemError
    
      ArducamUnkownError
    """
    ArducamInvalidParameter: typing.ClassVar[TOFErrorCode]  # value = <TOFErrorCode.ArducamInvalidParameter: 1>
    ArducamNoCache: typing.ClassVar[TOFErrorCode]  # value = <TOFErrorCode.ArducamNoCache: 2>
    ArducamNotImplemented: typing.ClassVar[TOFErrorCode]  # value = <TOFErrorCode.ArducamNotImplemented: 4>
    ArducamSkipFrame: typing.ClassVar[TOFErrorCode]  # value = <TOFErrorCode.ArducamSkipFrame: 240>
    ArducamSuccess: typing.ClassVar[TOFErrorCode]  # value = <TOFErrorCode.ArducamSuccess: 0>
    ArducamSystemError: typing.ClassVar[TOFErrorCode]  # value = <TOFErrorCode.ArducamSystemError: -2>
    ArducamUnkownDevice: typing.ClassVar[TOFErrorCode]  # value = <TOFErrorCode.ArducamUnkownDevice: 3>
    ArducamUnkownError: typing.ClassVar[TOFErrorCode]  # value = <TOFErrorCode.ArducamUnkownError: -1>
    __members__: typing.ClassVar[dict[str, TOFErrorCode]]  # value = {'ArducamSuccess': <TOFErrorCode.ArducamSuccess: 0>, 'ArducamInvalidParameter': <TOFErrorCode.ArducamInvalidParameter: 1>, 'ArducamNoCache': <TOFErrorCode.ArducamNoCache: 2>, 'ArducamUnkownDevice': <TOFErrorCode.ArducamUnkownDevice: 3>, 'ArducamNotImplemented': <TOFErrorCode.ArducamNotImplemented: 4>, 'ArducamSkipFrame': <TOFErrorCode.ArducamSkipFrame: 240>, 'ArducamSystemError': <TOFErrorCode.ArducamSystemError: -2>, 'ArducamUnkownError': <TOFErrorCode.ArducamUnkownError: -1>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    def str(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class TOFOutput:
    """
    Members:
    
      RAW
    
      DEPTH
    
      CONFIDENCE
    
      CACHE
    """
    CACHE: typing.ClassVar[TOFOutput]  # value = <TOFOutput.CACHE: 4>
    CONFIDENCE: typing.ClassVar[TOFOutput]  # value = <TOFOutput.CONFIDENCE: 1>
    DEPTH: typing.ClassVar[TOFOutput]  # value = <TOFOutput.DEPTH: 2>
    RAW: typing.ClassVar[TOFOutput]  # value = <TOFOutput.RAW: 0>
    __members__: typing.ClassVar[dict[str, TOFOutput]]  # value = {'RAW': <TOFOutput.RAW: 0>, 'DEPTH': <TOFOutput.DEPTH: 2>, 'CONFIDENCE': <TOFOutput.CONFIDENCE: 1>, 'CACHE': <TOFOutput.CACHE: 4>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class TofFrameWorkMode:
    """
    Members:
    
      SINGLE_FREQ_2PHASE
    
      SINGLE_FREQ_4PHASE
    
      SINGLE_FREQ_4PHASE_GRAY
    
      SINGLE_FREQ_4PHASE_BG
    
      SINGLE_FREQ_4PHASE_4BG
    
      SINGLE_FREQ_4PHASE_GRAY_5BG
    
      SINGLE_FREQ_GRAY_BG_4PHASE_GRAY_BG
    
      SINGLE_FREQ_GRAY_BG_4PHASE_BG
    
      SINGLE_FREQ_BG_GRAY_BG_4PHASE
    
      SINGLE_FREQ_BG_4PHASE_BG_GRAY
    
      DOUBLE_FREQ_4PHASE
    
      DOUBLE_FREQ_4PHASE_GRAY_4PHASE_BG
    
      DOUBLE_FREQ_4PHASE_4BG
    
      DOUBLE_FREQ_4PHASE_GRAY_5BG
    
      TRIPLE_FREQ_4PHASE
    
      TRIPLE_FREQ_4PHASE_GRAY_4PHASE_GRAY_4PHASE_BG
    
      QUAD_FREQ_4PHASE
    
      QUAD_FREQ_4PHASE_GRAY_4PHASE_BG_4PHASE_GRAY_4PHASE_BG
    
      BG_OUTDOOR
    
      GRAY_ONLY
    
      CUSTOM
    """
    BG_OUTDOOR: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.BG_OUTDOOR: 18>
    CUSTOM: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.CUSTOM: 20>
    DOUBLE_FREQ_4PHASE: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.DOUBLE_FREQ_4PHASE: 10>
    DOUBLE_FREQ_4PHASE_4BG: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.DOUBLE_FREQ_4PHASE_4BG: 12>
    DOUBLE_FREQ_4PHASE_GRAY_4PHASE_BG: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.DOUBLE_FREQ_4PHASE_GRAY_4PHASE_BG: 11>
    DOUBLE_FREQ_4PHASE_GRAY_5BG: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.DOUBLE_FREQ_4PHASE_GRAY_5BG: 13>
    GRAY_ONLY: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.GRAY_ONLY: 19>
    QUAD_FREQ_4PHASE: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.QUAD_FREQ_4PHASE: 16>
    QUAD_FREQ_4PHASE_GRAY_4PHASE_BG_4PHASE_GRAY_4PHASE_BG: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.QUAD_FREQ_4PHASE_GRAY_4PHASE_BG_4PHASE_GRAY_4PHASE_BG: 17>
    SINGLE_FREQ_2PHASE: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.SINGLE_FREQ_2PHASE: 0>
    SINGLE_FREQ_4PHASE: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.SINGLE_FREQ_4PHASE: 1>
    SINGLE_FREQ_4PHASE_4BG: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.SINGLE_FREQ_4PHASE_4BG: 4>
    SINGLE_FREQ_4PHASE_BG: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.SINGLE_FREQ_4PHASE_BG: 3>
    SINGLE_FREQ_4PHASE_GRAY: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.SINGLE_FREQ_4PHASE_GRAY: 2>
    SINGLE_FREQ_4PHASE_GRAY_5BG: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.SINGLE_FREQ_4PHASE_GRAY_5BG: 5>
    SINGLE_FREQ_BG_4PHASE_BG_GRAY: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.SINGLE_FREQ_BG_4PHASE_BG_GRAY: 9>
    SINGLE_FREQ_BG_GRAY_BG_4PHASE: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.SINGLE_FREQ_BG_GRAY_BG_4PHASE: 8>
    SINGLE_FREQ_GRAY_BG_4PHASE_BG: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.SINGLE_FREQ_GRAY_BG_4PHASE_BG: 7>
    SINGLE_FREQ_GRAY_BG_4PHASE_GRAY_BG: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.SINGLE_FREQ_GRAY_BG_4PHASE_GRAY_BG: 6>
    TRIPLE_FREQ_4PHASE: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.TRIPLE_FREQ_4PHASE: 14>
    TRIPLE_FREQ_4PHASE_GRAY_4PHASE_GRAY_4PHASE_BG: typing.ClassVar[TofFrameWorkMode]  # value = <TofFrameWorkMode.TRIPLE_FREQ_4PHASE_GRAY_4PHASE_GRAY_4PHASE_BG: 15>
    __members__: typing.ClassVar[dict[str, TofFrameWorkMode]]  # value = {'SINGLE_FREQ_2PHASE': <TofFrameWorkMode.SINGLE_FREQ_2PHASE: 0>, 'SINGLE_FREQ_4PHASE': <TofFrameWorkMode.SINGLE_FREQ_4PHASE: 1>, 'SINGLE_FREQ_4PHASE_GRAY': <TofFrameWorkMode.SINGLE_FREQ_4PHASE_GRAY: 2>, 'SINGLE_FREQ_4PHASE_BG': <TofFrameWorkMode.SINGLE_FREQ_4PHASE_BG: 3>, 'SINGLE_FREQ_4PHASE_4BG': <TofFrameWorkMode.SINGLE_FREQ_4PHASE_4BG: 4>, 'SINGLE_FREQ_4PHASE_GRAY_5BG': <TofFrameWorkMode.SINGLE_FREQ_4PHASE_GRAY_5BG: 5>, 'SINGLE_FREQ_GRAY_BG_4PHASE_GRAY_BG': <TofFrameWorkMode.SINGLE_FREQ_GRAY_BG_4PHASE_GRAY_BG: 6>, 'SINGLE_FREQ_GRAY_BG_4PHASE_BG': <TofFrameWorkMode.SINGLE_FREQ_GRAY_BG_4PHASE_BG: 7>, 'SINGLE_FREQ_BG_GRAY_BG_4PHASE': <TofFrameWorkMode.SINGLE_FREQ_BG_GRAY_BG_4PHASE: 8>, 'SINGLE_FREQ_BG_4PHASE_BG_GRAY': <TofFrameWorkMode.SINGLE_FREQ_BG_4PHASE_BG_GRAY: 9>, 'DOUBLE_FREQ_4PHASE': <TofFrameWorkMode.DOUBLE_FREQ_4PHASE: 10>, 'DOUBLE_FREQ_4PHASE_GRAY_4PHASE_BG': <TofFrameWorkMode.DOUBLE_FREQ_4PHASE_GRAY_4PHASE_BG: 11>, 'DOUBLE_FREQ_4PHASE_4BG': <TofFrameWorkMode.DOUBLE_FREQ_4PHASE_4BG: 12>, 'DOUBLE_FREQ_4PHASE_GRAY_5BG': <TofFrameWorkMode.DOUBLE_FREQ_4PHASE_GRAY_5BG: 13>, 'TRIPLE_FREQ_4PHASE': <TofFrameWorkMode.TRIPLE_FREQ_4PHASE: 14>, 'TRIPLE_FREQ_4PHASE_GRAY_4PHASE_GRAY_4PHASE_BG': <TofFrameWorkMode.TRIPLE_FREQ_4PHASE_GRAY_4PHASE_GRAY_4PHASE_BG: 15>, 'QUAD_FREQ_4PHASE': <TofFrameWorkMode.QUAD_FREQ_4PHASE: 16>, 'QUAD_FREQ_4PHASE_GRAY_4PHASE_BG_4PHASE_GRAY_4PHASE_BG': <TofFrameWorkMode.QUAD_FREQ_4PHASE_GRAY_4PHASE_BG_4PHASE_GRAY_4PHASE_BG: 17>, 'BG_OUTDOOR': <TofFrameWorkMode.BG_OUTDOOR: 18>, 'GRAY_ONLY': <TofFrameWorkMode.GRAY_ONLY: 19>, 'CUSTOM': <TofFrameWorkMode.CUSTOM: 20>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    @typing.overload
    def __int__(self) -> int:
        ...
    @typing.overload
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class TofWorkMode:
    """
    Members:
    
      SINGLE_FREQ
    
      DOUBLE_FREQ
    
      TRIPLE_FREQ
    
      QUAD_FREQ
    
      DISTANCE
    
      HDR
    
      AE
    
      BG_OUTDOOR
    
      GRAY_ONLY
    
      CUSTOM1
    
      CUSTOM2
    
      CUSTOM3
    """
    AE: typing.ClassVar[TofWorkMode]  # value = <TofWorkMode.AE: 6>
    BG_OUTDOOR: typing.ClassVar[TofWorkMode]  # value = <TofWorkMode.BG_OUTDOOR: 7>
    CUSTOM1: typing.ClassVar[TofWorkMode]  # value = <TofWorkMode.CUSTOM1: 9>
    CUSTOM2: typing.ClassVar[TofWorkMode]  # value = <TofWorkMode.CUSTOM2: 10>
    CUSTOM3: typing.ClassVar[TofWorkMode]  # value = <TofWorkMode.CUSTOM3: 11>
    DISTANCE: typing.ClassVar[TofWorkMode]  # value = <TofWorkMode.DISTANCE: 4>
    DOUBLE_FREQ: typing.ClassVar[TofWorkMode]  # value = <TofWorkMode.DOUBLE_FREQ: 1>
    GRAY_ONLY: typing.ClassVar[TofWorkMode]  # value = <TofWorkMode.GRAY_ONLY: 8>
    HDR: typing.ClassVar[TofWorkMode]  # value = <TofWorkMode.HDR: 5>
    QUAD_FREQ: typing.ClassVar[TofWorkMode]  # value = <TofWorkMode.QUAD_FREQ: 3>
    SINGLE_FREQ: typing.ClassVar[TofWorkMode]  # value = <TofWorkMode.SINGLE_FREQ: 0>
    TRIPLE_FREQ: typing.ClassVar[TofWorkMode]  # value = <TofWorkMode.TRIPLE_FREQ: 2>
    __members__: typing.ClassVar[dict[str, TofWorkMode]]  # value = {'SINGLE_FREQ': <TofWorkMode.SINGLE_FREQ: 0>, 'DOUBLE_FREQ': <TofWorkMode.DOUBLE_FREQ: 1>, 'TRIPLE_FREQ': <TofWorkMode.TRIPLE_FREQ: 2>, 'QUAD_FREQ': <TofWorkMode.QUAD_FREQ: 3>, 'DISTANCE': <TofWorkMode.DISTANCE: 4>, 'HDR': <TofWorkMode.HDR: 5>, 'AE': <TofWorkMode.AE: 6>, 'BG_OUTDOOR': <TofWorkMode.BG_OUTDOOR: 7>, 'GRAY_ONLY': <TofWorkMode.GRAY_ONLY: 8>, 'CUSTOM1': <TofWorkMode.CUSTOM1: 9>, 'CUSTOM2': <TofWorkMode.CUSTOM2: 10>, 'CUSTOM3': <TofWorkMode.CUSTOM3: 11>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    @typing.overload
    def __int__(self) -> int:
        ...
    @typing.overload
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
__version__: str = 'dev'
