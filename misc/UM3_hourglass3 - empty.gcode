;START_OF_HEADER
;HEADER_VERSION:0.1
;FLAVOR:Griffin
;GENERATOR.NAME:Cura_SteamEngine
;GENERATOR.VERSION:4.5.0
;GENERATOR.BUILD_DATE:2020-02-25
;TARGET_MACHINE.NAME:Ultimaker 3
;EXTRUDER_TRAIN.0.INITIAL_TEMPERATURE:210
;EXTRUDER_TRAIN.0.MATERIAL.VOLUME_USED:7675
;EXTRUDER_TRAIN.0.MATERIAL.GUID:532e8b3d-5fd4-4149-b936-53ada9bd6b85
;EXTRUDER_TRAIN.0.NOZZLE.DIAMETER:0.4
;EXTRUDER_TRAIN.0.NOZZLE.NAME:AA 0.4
;BUILD_PLATE.TYPE:glass
;BUILD_PLATE.INITIAL_TEMPERATURE:60
;PRINT.TIME:3875
;PRINT.GROUPS:1
;PRINT.SIZE.MIN.X:9
;PRINT.SIZE.MIN.Y:6
;PRINT.SIZE.MIN.Z:0.27
;PRINT.SIZE.MAX.X:136.286
;PRINT.SIZE.MAX.Y:122.296
;PRINT.SIZE.MAX.Z:59.97
;END_OF_HEADER
;Generated with Cura_SteamEngine 4.5.0
T0
M82 ;absolute extrusion mode

G92 E0
M109 S210
G0 F15000 X9 Y6 Z2
G280
G1 F1500 E-6.5
M109 S120
G1 X100 Y100

G4 S300

M140 S0
M204 S3000
M205 X20 Y20
M107
G91 ;Relative movement
G0 F15000 X8.0 Z0.5 E-4.5 ;Wiping+material retraction
G0 F10000 Z1.5 E4.5 ;Compensation for the retraction
G90 ;Disable relative movement
M82 ;absolute extrusion mode
M104 S0
M104 T1 S0
;End of Gcode
;SETTING_3 {"extruder_quality": ["[general]\\nversion = 4\\nname = Fast #2\\ndef
;SETTING_3 inition = ultimaker3\\n\\n[metadata]\\nposition = 0\\ntype = quality_
;SETTING_3 changes\\nquality_type = draft\\n\\n[values]\\ninfill_pattern = lines
;SETTING_3 \\ninfill_sparse_density = 0\\nspeed_print = 30\\ntop_thickness = 0\\
;SETTING_3 n\\n", "[general]\\nversion = 4\\nname = Fast #2\\ndefinition = ultim
;SETTING_3 aker3\\n\\n[metadata]\\nposition = 1\\ntype = quality_changes\\nquali
;SETTING_3 ty_type = draft\\n\\n[values]\\nsupport_infill_rate = =15 if support_
;SETTING_3 enable else 0 if support_tree_enable else 15\\n\\n"], "global_quality
;SETTING_3 ": "[general]\\nversion = 4\\nname = Fast #2\\ndefinition = ultimaker
;SETTING_3 3\\n\\n[metadata]\\ntype = quality_changes\\nquality_type = draft\\n\
;SETTING_3 \n[values]\\nadhesion_extruder_nr = 1\\nadhesion_type = none\\nlayer_
;SETTING_3 height = 0.3\\nsupport_extruder_nr = 1\\nsupport_type = buildplate\\n
;SETTING_3 \\n"}
