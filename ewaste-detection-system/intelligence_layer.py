class EWasteIntelligence:
    def __init__(self):
        # Database mapping class names to intelligence data
        self.intelligence_db = {
            # MOBILE & CONSUMER DEVICES
            'smartphone': {
                'material_composition': ['Glass', 'Plastic', 'Lithium-ion Battery', 'Copper', 'Gold', 'Silicon'],
                'recycling_type': 'High Value Recyclable',
                'carbon_recovery_benefit': 'High (Gold, Cobalt recovery)',
                'reuse_potential': 'Refurbishable, Resale, Parts Salvage',
                'hazard_flag': True, 
                'hazard_reason': 'Lithium-ion Battery (Fire Risk)'
            },
            'feature_phone': {
                'material_composition': ['Plastic', 'Keypad (Rubber/Plastic)', 'Lithium-ion Battery', 'Copper', 'Circuit Board'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Medium',
                'reuse_potential': 'Resale, Metal Recovery',
                'hazard_flag': True,
                'hazard_reason': 'Lithium-ion Battery'
            },
            'tablet': {
                'material_composition': ['Glass', 'Aluminum/Plastic', 'Lithium-ion Battery', 'Copper', 'Gold'],
                'recycling_type': 'High Value Recyclable',
                'carbon_recovery_benefit': 'High',
                'reuse_potential': 'Refurbishable, Screen Salvage',
                'hazard_flag': True,
                'hazard_reason': 'Lithium-ion Battery'
            },
            'smartwatch': {
                'material_composition': ['Glass', 'Silicon/Metal Strap', 'Lithium-ion Battery', 'Sensors'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Low-Medium',
                'reuse_potential': 'Refurbishable',
                'hazard_flag': True,
                'hazard_reason': 'Small Lithium Battery'
            },
            'earbuds': {
                'material_composition': ['Plastic', 'Tiny Lithium Battery', 'Copper Coil', 'Magnet'],
                'recycling_type': 'Difficult to Recycle (Mixed materials)',
                'carbon_recovery_benefit': 'Low',
                'reuse_potential': 'Sanitization & Resale (Limited)',
                'hazard_flag': True,
                'hazard_reason': 'Lithium Battery ingestion risk/fire'
            },
            'headphones': {
                'material_composition': ['Plastic', 'Foam', 'Copper Wire', 'Magnet', 'Drivers'],
                'recycling_type': 'Recyclable (Plastics/Metals)',
                'carbon_recovery_benefit': 'Medium',
                'reuse_potential': 'Refurbishable, Audio Driver Salvage',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'bluetooth_speaker': {
                'material_composition': ['Plastic/Metal Mesh', 'Lithium-ion Battery', 'Magnet', 'Copper'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Medium',
                'reuse_potential': 'Refurbishable',
                'hazard_flag': True,
                'hazard_reason': 'Lithium-ion Battery'
            },
            'power_bank': {
                'material_composition': ['Lithium-ion/Polymer Cells', 'Plastic/Metal Casing', 'Circuit Board'],
                'recycling_type': 'Hazardous Recyclable',
                'carbon_recovery_benefit': 'High (Cobalt/Lithium)',
                'reuse_potential': 'Cell Salvage (Experts Only)',
                'hazard_flag': True,
                'hazard_reason': 'High Capacity Lithium Battery (Fire/Explosion Risk)'
            },

            # COMPUTING DEVICES
            'laptop': {
                'material_composition': ['Aluminum/Plastic', 'Glass (Screen)', 'Lithium Battery', 'Copper (Heat pipe)', 'Gold (PCB)'],
                'recycling_type': 'High Value Recyclable',
                'carbon_recovery_benefit': 'Very High',
                'reuse_potential': 'Refurbishable, Part Salvage (RAM, SSD, Screen)',
                'hazard_flag': True,
                'hazard_reason': 'Lithium Battery'
            },
            'desktop_cpu': {
                'material_composition': ['Steel/Aluminum Case', 'Detailed PCBs', 'Power Supply', 'Fans'],
                'recycling_type': 'High Value Recyclable',
                'carbon_recovery_benefit': 'High (Steel, Copper, Gold)',
                'reuse_potential': 'Refurbishable, Component Salvage',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'all_in_one_pc': {
                'material_composition': ['Glass', 'Plastic', 'Aluminum', 'Circuit Boards'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'High',
                'reuse_potential': 'Refurbishable',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'monitor': {
                'material_composition': ['Glass (LCD/LED)', 'Plastic', 'Circuit Board', 'Fluorescent Backlight (Old models)'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Medium',
                'reuse_potential': 'Refurbishable',
                'hazard_flag': True,
                'hazard_reason': 'Mercury in CCFL backlights (older models) / Capacitors'
            },
            'keyboard': {
                'material_composition': ['Plastic (ABS)', 'Circuit Sheet', 'Rubber Domes', 'USB Cable'],
                'recycling_type': 'Recyclable (Plastics)',
                'carbon_recovery_benefit': 'Low',
                'reuse_potential': 'Resale, Keycap Salvage',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'mouse': {
                'material_composition': ['Plastic', 'Optical Sensor', 'PCB', 'USB Cable/Battery'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Low',
                'reuse_potential': 'Resale',
                'hazard_flag': False, # Unless wireless with battery
                'hazard_reason': None
            },
            'trackpad': {
                 'material_composition': ['Glass/Plastic Surface', 'PCB', 'Digitizer'],
                 'recycling_type': 'Recyclable',
                 'carbon_recovery_benefit': 'Low',
                 'reuse_potential': 'Part Salvage',
                 'hazard_flag': False,
                 'hazard_reason': None
            },
            'printer': {
                'material_composition': ['Plastic', 'Steel', 'Motors', 'Circuit Board'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Medium',
                'reuse_potential': 'Refurbishable, Motor/Rod Salvage',
                'hazard_flag': True,
                'hazard_reason': 'Toner/Ink Cartridges (Chemical Hazard)'
            },
            'scanner': {
                'material_composition': ['Glass', 'Plastic', 'CCD Sensor', 'Motors'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Medium',
                'reuse_potential': 'Resale',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'router': {
                'material_composition': ['Plastic', 'PCB', 'Antennas'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Low-Medium',
                'reuse_potential': 'Resale, Flash Memory Reuse (OpenWRT)',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'modem': {
                'material_composition': ['Plastic', 'PCB'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Low',
                'reuse_potential': 'Resale',
                'hazard_flag': False,
                'hazard_reason': None
            },

            # INTERNAL HARDWARE
            'motherboard': {
                'material_composition': ['Fiberglass (FR4)', 'Copper Traces', 'Gold Plated Pins', 'Solder (Lead/Tin)', 'Capacitors'],
                'recycling_type': 'High Value Hazardous Recyclable',
                'carbon_recovery_benefit': 'Very High (Gold/Copper)',
                'reuse_potential': 'Resale if functional',
                'hazard_flag': True,
                'hazard_reason': 'Lead Solder, Beryllium (sometimes)'
            },
            'circuit_board': { # Generic PCB
                'material_composition': ['Fiberglass', 'Copper', 'Solder', 'Components'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Medium',
                'reuse_potential': 'Component Desoldering',
                'hazard_flag': True,
                'hazard_reason': 'Lead Solder'
            },
            'gpu': {
                'material_composition': ['PCB', 'Silicon Die', 'Aluminum Heatsink', 'Fans', 'Gold', 'Copper'],
                'recycling_type': 'High Value Recyclable',
                'carbon_recovery_benefit': 'Very High',
                'reuse_potential': 'Resale (High Demand), Chip Salvage',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'cpu_chip': {
                'material_composition': ['Silicon', 'Gold Pins', 'Ceramic/Fiberglass Substrate', 'Copper Heat Spreader'],
                'recycling_type': 'Precious Metal Recovery',
                'carbon_recovery_benefit': 'Very High (Gold)',
                'reuse_potential': 'Resale, Keychains (if dead)',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'ram_module': {
                'material_composition': ['PCB', 'Gold Fingers', 'Silicon Memory Chips'],
                'recycling_type': 'High Value Recyclable',
                'carbon_recovery_benefit': 'High (Gold)',
                'reuse_potential': 'Resale',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'hard_disk_drive': {
                'material_composition': ['Aluminum Case', 'Rare Earth Magnets (Neodymium)', 'Platters (Glass/Aluminum)', 'PCB'],
                'recycling_type': 'Magnet/Aluminum Recovery',
                'carbon_recovery_benefit': 'High',
                'reuse_potential': 'Magnet Salvage, Platter Art',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'ssd_drive': {
                'material_composition': ['PCB', 'NAND Flash Chips', 'Controller Chip'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Medium',
                'reuse_potential': 'Resale (Wipe Data First)',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'power_supply_unit': {
                'material_composition': ['Steel Box', 'Copper Transformers', 'Capacitors', 'Wires'],
                'recycling_type': 'Metal Recovery',
                'carbon_recovery_benefit': 'Medium',
                'reuse_potential': 'Functional Reuse',
                'hazard_flag': True,
                'hazard_reason': 'High Voltage Capacitors (Shock Risk)'
            },
            'cooling_fan': {
                'material_composition': ['Plastic', 'Copper Motor Coils', 'Magnet'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Low',
                'reuse_potential': 'Reuse in DIY projects',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'heat_sink': {
                'material_composition': ['Aluminum' or 'Copper'],
                'recycling_type': 'Pure Metal Recycling',
                'carbon_recovery_benefit': 'High (Energy saving vs virgin metal)',
                'reuse_potential': 'Reuse',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'expansion_card': {
                'material_composition': ['PCB', 'Steel Bracket', 'Chips'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Medium',
                'reuse_potential': 'Resale',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'network_card': {
                'material_composition': ['PCB', 'Chips', 'Metal Shielding'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Low',
                'reuse_potential': 'Resale',
                'hazard_flag': False,
                'hazard_reason': None
            },

            # POWER & CABLES
            'charger': {
                'material_composition': ['Plastic Shell', 'PCB', 'Copper Transformer'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Low',
                'reuse_potential': 'Reuse if standard connector',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'adapter': { # Similar to charger
                'material_composition': ['Plastic', 'Copper', 'PCB'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Low',
                'reuse_potential': 'Reuse',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'usb_cable': {
                'material_composition': ['PVC/TPE Jacket', 'Copper Wire', 'Shielding Foil'],
                'recycling_type': 'Wire Chopping (Copper Recovery)',
                'carbon_recovery_benefit': 'Medium',
                'reuse_potential': 'Reuse',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'hdmi_cable': {
                'material_composition': ['PVC', 'Copper', 'Gold Plated Connectors'],
                'recycling_type': 'Wire Chopping',
                'carbon_recovery_benefit': 'Medium',
                'reuse_potential': 'Reuse',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'ethernet_cable': {
                'material_composition': ['PVC', 'Copper (Twisted Pairs)'],
                'recycling_type': 'Wire Chopping',
                'carbon_recovery_benefit': 'Medium',
                'reuse_potential': 'Reuse',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'power_cable': {
                'material_composition': ['PVC', 'Thick Copper Wire'],
                'recycling_type': 'High Copper Recovery',
                'carbon_recovery_benefit': 'High',
                'reuse_potential': 'Reuse',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'extension_board': {
                'material_composition': ['Plastic', 'Copper Strips', 'Switches'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Medium',
                'reuse_potential': 'Reuse',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'battery': { # General Alkaline or NiMH
                'material_composition': ['Zinc', 'Manganese', 'Steel', 'Potassium Hydroxide'],
                'recycling_type': 'Hazardous Recyclable',
                'carbon_recovery_benefit': 'Medium',
                'reuse_potential': 'None (Recycle Only)',
                'hazard_flag': True,
                'hazard_reason': 'Chemical Leakage'
            },
            'lithium_battery': {
                'material_composition': ['Lithium', 'Cobalt', 'Nickel', 'Graphite', 'Electrolyte'],
                'recycling_type': 'Hazardous High Value',
                'carbon_recovery_benefit': 'High',
                'reuse_potential': 'Grid Storage (if capacity remains)',
                'hazard_flag': True,
                'hazard_reason': 'Fire/Explosion Risk'
            },
            'ups_unit': {
                'material_composition': ['Lead-Acid Battery', 'Plastic', 'PCB', 'Transformers'],
                'recycling_type': 'Hazardous (Lead)',
                'carbon_recovery_benefit': 'High (Lead recovery)',
                'reuse_potential': 'Replace Battery & Reuse',
                'hazard_flag': True,
                'hazard_reason': 'Lead-Acid Battery (Toxic/Heavy)'
            },

            # LARGE ELECTRONICS
            'television': {
                'material_composition': ['Panel (LCD/OLED)', 'Plastic', 'Circuit Boards', 'Speakers'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Medium',
                'reuse_potential': 'Refurbishable',
                'hazard_flag': True,
                'hazard_reason': 'Capacitors, potential Mercury (old units)'
            },
            'microwave': {
                'material_composition': ['Steel', 'Magnetron', 'Transformer', 'Glass', 'Capacitor'],
                'recycling_type': 'Scrap Metal Recovery',
                'carbon_recovery_benefit': 'High',
                'reuse_potential': 'Parts Salvage (Magnetron/Transformer)',
                'hazard_flag': True,
                'hazard_reason': 'High Voltage Capacitor (Lethal Shock Risk)'
            },
            'refrigerator_control_board': {
                'material_composition': ['PCB', 'Relays', 'Capacitors'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Low',
                'reuse_potential': 'Repair Refrigerator',
                'hazard_flag': False,
                'hazard_reason': None
            },
            'washing_machine_panel': {
                'material_composition': ['Plastic', 'PCB', 'Buttons'],
                'recycling_type': 'Recyclable',
                'carbon_recovery_benefit': 'Low',
                'reuse_potential': 'Repair Washing Machine',
                'hazard_flag': False,
                'hazard_reason': None
            }
        }

    def analyze(self, class_name, confidence):
        """
        Analyzes a detected object and returns detailed recycling and hazard info.
        """
        data = self.intelligence_db.get(class_name)
        
        if not data:
            return {
                'class': class_name,
                'confidence': confidence,
                'error': 'No intelligence data available for this class.'
            }

        return {
            'class': class_name,
            'confidence': f"{confidence:.2f}",
            'material_composition': data['material_composition'],
            'recycling_recommendation': data['recycling_type'],
            'reuse_suggestion': data['reuse_potential'],
            'environmental_impact': {
                'carbon_recovery_benefit': data['carbon_recovery_benefit'],
            },
            'safety_alert': {
                'is_hazardous': data['hazard_flag'],
                'hazard_details': data['hazard_reason']
            }
        }
