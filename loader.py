#!/usr/bin/env python

from mrcrowbar import models as mrc
from mrcrowbar import bits, utils

from collections import namedtuple

TI_028X_LATER_ENERGY = (0,  1,  2,  3,  4,  6,  8, 11,
                       16, 23, 33, 47, 63, 85,114, 0)
TI_5110_PITCH = (0,  15,  16,  17,  19,  21,  22,  25,
                26,  29,  32,  36,  40,  42,  46,  50,
                55,  60,  64,  68,  72,  76,  80,  84,
                86,  93, 101, 110, 120, 132, 144, 159)
TI_5220_PITCH = (0,  15,  16,  17,  18,  19,  20,  21,
                22,  23,  24,  25,  26,  27,  28,  29,
                30,  31,  32,  33,  34,  35,  36,  37,
                38,  39,  40,  41,  42,  44,  46,  48,
                50,  52,  53,  56,  58,  60,  62,  65,
                68,  70,  72,  76,  78,  80,  84,  86,
                91,  94,  98, 101, 105, 109, 114, 118,
                122, 127, 132, 137, 142, 148, 153, 159)
TI_5110_5220_LPC = (
# K1
        ( -501, -498, -497, -495, -493, -491, -488, -482,
          -478, -474, -469, -464, -459, -452, -445, -437,
          -412, -380, -339, -288, -227, -158,  -81,   -1,
            80,  157,  226,  287,  337,  379,  411,  436 ),
# K2
        ( -328, -303, -274, -244, -211, -175, -138,  -99,
           -59,  -18,   24,   64,  105,  143,  180,  215,
           248,  278,  306,  331,  354,  374,  392,  408,
           422,  435,  445,  455,  463,  470,  476,  506 ),
# K3
        ( -441, -387, -333, -279, -225, -171, -117,  -63,
            -9,   45,   98,  152,  206,  260,  314,  368  ),
# K4
        ( -328, -273, -217, -161, -106,  -50,    5,   61,
           116,  172,  228,  283,  339,  394,  450,  506  ),
# K5
        ( -328, -282, -235, -189, -142,  -96,  -50,   -3,
            43,   90,  136,  182,  229,  275,  322,  368  ),
# K6
        ( -256, -212, -168, -123,  -79,  -35,   10,   54,
            98,  143,  187,  232,  276,  320,  365,  409  ),
# K7
        ( -308, -260, -212, -164, -117,  -69,  -21,   27,
            75,  122,  170,  218,  266,  314,  361,  409  ),
# K8
        ( -256, -161,  -66,   29,  124,  219,  314,  409  ),
# K9
        ( -256, -176,  -96,  -15,   65,  146,  226,  307  ),
# K10
        ( -205, -132,  -59,   14,   87,  160,  234,  307  ),
)

TI_CHIPS = {
    'tms5110': {
        'energy_bits': 4,
        'repeat_bits': 1,
        'pitch_bits': 5,
        'k_bits': [5, 5, 4, 4, 4, 4, 4, 3, 3, 3],
        'energy_lut': TI_028X_LATER_ENERGY,
        'pitch_lut': TI_5110_PITCH,
        'k_lut': TI_5110_5220_LPC
    },
    'tms5220': {
        'energy_bits': 4,
        'repeat_bits': 1,
        'pitch_bits': 6,
        'k_bits': [5, 5, 4, 4, 4, 4, 4, 3, 3, 3],
        'energy_lut': TI_028X_LATER_ENERGY,
        'pitch_lut': TI_5220_PITCH,
        'k_lut': TI_5110_5220_LPC
     }
}



find_closest_index = lambda source, value: source.index( sorted( source, key=lambda x: abs(x - value) )[0] )


VoicedFrame = namedtuple( 'VoicedFrame', ['energy', 'pitch', 'k1', 'k2', 'k3', 'k4', 'k5', 'k6', 'k7', 'k8', 'k9', 'k10'] )
UnvoicedFrame = namedtuple( 'UnvoicedFrame', ['energy', 'k1', 'k2', 'k3', 'k4'] )
RepeatedFrame = namedtuple( 'RepeatedFrame', ['energy', 'pitch'] )
SilentFrame = namedtuple( 'SilentFrame', [] )
StopFrame = namedtuple( 'StopFrame', [] )


class TMSStream( mrc.View ):
    def __init__( self, parent, data_ref ):
        super().__init__( parent )
        self._data = data_ref

    data = mrc.view_property( '_data' )

    def import_data( self, frames, chip ):
        bs = bits.BitStream( io_endian='big', bit_endian='little' )

        if chip not in TI_CHIPS:
            raise ValueError( '{} not a supported chip: options are {}'.format(chip, TI_CHIPS.keys()) )
        chip = TI_CHIPS[chip]

        for frame in frames:
            if isinstance( frame, SilentFrame ):
                bs.write( 0, chip['energy_bits'] )
            elif isinstance( frame, StopFrame ):
                bs.write( (1 << chip['energy_bits']) - 1, chip['energy_bits'] )
            elif isinstance( frame, RepeatedFrame ):
                bs.write( find_closest_index( chip['energy_lut'], frame.energy ), chip['energy_bits'] )
                bs.write( 1, chip['repeat_bits'] )
                bs.write( find_closest_index( chip['pitch_lut'], frame.pitch ), chip['pitch_bits'] )
            elif isinstance( frame, UnvoicedFrame ):
                bs.write( find_closest_index( chip['energy_lut'], frame.energy ), chip['energy_bits'] )
                bs.write( 0, chip['repeat_bits'] )
                bs.write( 0, chip['pitch_bits'] )
                bs.write( find_closest_index( chip['k_lut'][0], frame.k1 ), chip['k_bits'][0] )
                bs.write( find_closest_index( chip['k_lut'][1], frame.k2 ), chip['k_bits'][1] )
                bs.write( find_closest_index( chip['k_lut'][2], frame.k3 ), chip['k_bits'][2] )
                bs.write( find_closest_index( chip['k_lut'][3], frame.k4 ), chip['k_bits'][3] )
            elif isinstance( frame, VoicedFrame ):
                bs.write( find_closest_index( chip['energy_lut'], frame.energy ), chip['energy_bits'] )
                bs.write( 0, chip['repeat_bits'] )
                bs.write( find_closest_index( chip['pitch_lut'], frame.pitch ), chip['pitch_bits'] )
                bs.write( find_closest_index( chip['k_lut'][0], frame.k1 ), chip['k_bits'][0] )
                bs.write( find_closest_index( chip['k_lut'][1], frame.k2 ), chip['k_bits'][1] )
                bs.write( find_closest_index( chip['k_lut'][2], frame.k3 ), chip['k_bits'][2] )
                bs.write( find_closest_index( chip['k_lut'][3], frame.k4 ), chip['k_bits'][3] )
                bs.write( find_closest_index( chip['k_lut'][4], frame.k5 ), chip['k_bits'][4] )
                bs.write( find_closest_index( chip['k_lut'][5], frame.k6 ), chip['k_bits'][5] )
                bs.write( find_closest_index( chip['k_lut'][6], frame.k7 ), chip['k_bits'][6] )
                bs.write( find_closest_index( chip['k_lut'][7], frame.k8 ), chip['k_bits'][7] )
                bs.write( find_closest_index( chip['k_lut'][8], frame.k9 ), chip['k_bits'][8] )
                bs.write( find_closest_index( chip['k_lut'][9], frame.k10 ), chip['k_bits'][9] )

        self.data = bs.get_buffer()

    def export_data( self, chip ):
        frames = []
        bs = bits.BitStream( self.data, io_endian='big', bit_endian='little' )

        if chip not in TI_CHIPS:
            raise ValueError( '{} not a supported chip: options are {}'.format(chip, TI_CHIPS.keys()) )
        chip = TI_CHIPS[chip]

        while bs.in_bounds():
            energy = bs.read( chip['energy_bits'] )
            if energy == 0:
                frames.append( SilentFrame() )
                continue
            if energy == (1 << chip['energy_bits']) - 1:
                frames.append( StopFrame() )
                break
            repeat = bs.read( chip['repeat_bits'] )
            pitch = bs.read( chip['pitch_bits'] )
            if repeat:
                frames.append( RepeatedFrame( energy=chip['energy_lut'][energy], pitch=chip['pitch_lut'][pitch] ) )
                continue
            k1 = bs.read( chip['k_bits'][0] )
            k2 = bs.read( chip['k_bits'][1] )
            k3 = bs.read( chip['k_bits'][2] )
            k4 = bs.read( chip['k_bits'][3] )
            if pitch == 0:
                frames.append( UnvoicedFrame( 
                    energy=chip['energy_lut'][energy],
                    k1=chip['k_lut'][0][k1],
                    k2=chip['k_lut'][1][k2],
                    k3=chip['k_lut'][2][k3],
                    k4=chip['k_lut'][3][k4]
                ) )
                continue

            k5 = bs.read( chip['k_bits'][4] )
            k6 = bs.read( chip['k_bits'][5] )
            k7 = bs.read( chip['k_bits'][6] )
            k8 = bs.read( chip['k_bits'][7] )
            k9 = bs.read( chip['k_bits'][8] )
            k10 = bs.read( chip['k_bits'][9] )
            frames.append( VoicedFrame( 
                energy=chip['energy_lut'][energy],
                pitch=chip['pitch_lut'][pitch],
                k1=chip['k_lut'][0][k1],
                k2=chip['k_lut'][1][k2],
                k3=chip['k_lut'][2][k3],
                k4=chip['k_lut'][3][k4],
                k5=chip['k_lut'][4][k5],
                k6=chip['k_lut'][5][k6],
                k7=chip['k_lut'][6][k7],
                k8=chip['k_lut'][7][k8],
                k9=chip['k_lut'][8][k9],
                k10=chip['k_lut'][9][k10]
            ) )
        if bs.tell()[0] != len( self.data ):
            print( 'Warning: {} trailing bytes unused'.format( len( self.data ) - bs.tell()[0] ) )
            utils.hexdump( self.data, start=bs.tell()[0] )
        return frames


class SpeechSample( mrc.Block ):
    data = mrc.Bytes( 0x00 )

    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        self.commands = TMSStream( self, mrc.Ref( 'data' ) )


class SpeechROM( mrc.Block ):
    index_end = mrc.UInt16_LE( 0x00 )

    @property
    def index_length( self ): 
        return (self.index_end - 2) // 2 
    
    @index_length.setter 
    def index_length( self, value ): 
        self.index_end = value * 2 + 2 
  
    index = mrc.UInt16_LE( 0x02, count=mrc.Ref( 'index_length' ) ) 
    data = mrc.Bytes( mrc.EndOffset( 'index' ) ) 
    def __init__( self, *args, **kwargs ): 
        super().__init__( *args, **kwargs ) 
        self.samples = mrc.LinearStore( self, mrc.Ref( 'data' ), SpeechSample, offsets=mrc.Ref( 'index' ), base_offset=mrc.EndOffset( 'index', neg=True ) ) 


