var dagfuncs = (window.dashAgGridFunctions = window.dashAgGridFunctions || {});

// Set dropdowns for certain items' value column. 
dagfuncs.dynamicCellEditor = function (params, modifier) {
    const item = params.data.Name;
    if (item === 'rLinkType') {
        if (modifier === 'Face') {
            return {
                component: 'agSelectCellEditor',
                params: {values: ['ThermalResistance', 'Heat Transfer Coefficient']},
            }
        }
        return {
            component: 'agSelectCellEditor',
            params: {values: ['ThermalResistance']},
        }
    }

    else if (item === 'ThermalParameters') {
        return {
            component: 'agSelectCellEditor',
            params: {values: ['Power', 'Temperature']},
        }
    }

    else if (item === 'ResistanceChoice') {
        return {
            component: 'agSelectCellEditor',
            params: {values: ['Specified', 'Compute', 'NoResistance']},
        }
    }

    return 'agTextCellEditor'
};

// Set which rows can be editable or not 
dagfuncs.editable = function (params, type) {
    value = params.data.Name
    if (type === 'Node') {
        if (value === 'FaceID') {
            return false
        }
        else if (value === 'Type') {
            return false
        }
        else {
            return true
        }
    }
    
    else if (type === 'Link') {
        if (value === 'LinkType') {
            return false
        }
        else if (value === 'source') {
            return false
        }
        else if (value === 'target') {
            return false
        }
        else if (value === 'Node 1') {
            return false
        }
        else if (value === 'Node 2') {
            return false
        }
        else {
            return true
        }
        
    }
    
    else if (type === 'Units'){
        return editUnitsBox(value)
    }

   return true
};

// Set which items have open cell editing vs dropdown
dagfuncs.unitsDropdown = function (params) {
    const item = params.data.Name;
    const mass_units = ['ug', 
                        'mg', 
                        'gram', 
                        'kg', 
                        'ton', 
                        'oz', 
                        'lb']

    const specific_heat_units = ['mJ_per_Kelkg',
                                'J_per_Kelkg',
                                'J_per_Celkg',
                                'kG_per_Kelkg',
                                'btu_per_IbmFah',
                                'btu_per_IbmRank',
                                'cal_per_gKel',
                                'cal_per_gCel',
                                'erg_per_gKel',
                                'kcal_per_kgKel',
                                'kcal_per_kgCel']

    const power_units = ['fW',
                        'pW',
                        'nW',
                        'uW',
                        'mW',
                        'W',
                        'kW',
                        'megW',
                        'gW',
                        'Btu_per_hr',
                        'Btu_per_sec',
                        'dBm',
                        'dBW',
                        'HP',
                        'erg_per_sec']

    //Temperature units for Boundary Nodes
    const temperature_units = ['mkel',
                                'ckel',
                                'dkel',
                                'kel',
                                'cel',
                                'rank',
                                'fah']
    // C-Link units
    const mass_flow_units = ['g_per_s',
                            'kg_per_s',
                            'Ibm_per_min',
                            'Ibm_per_s']

    //R-Link Units
    const heat_units = ['Kel_per_W',
                        'cel_per_W',
                        'FahSec_per_btu',
                        'Kels_per_J']

    // Thermal resistance units
    const thermal_resistance_units = ['Kel_per_W',
                                      'cel_per_W',
                                      'FahSec_per_btu',
                                      'Kels_per_J']

    // const thickness_units = ['f',
    //                          'p',
    //                          'n',
    //                          'u',
    //                          'm',
    //                          ' ',
    //                          'k',
    //                          'meg',
    //                          'g',
    //                          't',]

    const thickness_units = ['fm',
                             'pm',
                             'nm',
                             'um',
                             'mm',
                             'cm',
                             'dm',
                             'meter',
                             'km',
                             'uin',
                             'in',
                             'ft',
                             'yd',
                             'mile',
                             'lightyear',
                             'mileNaut',
                             'mileTerr']

    const heat_transfer_coefficient_units = ['w_per_m2kel',
                                             'w_per_m2Cel',
                                             'btu_per_rankHrFt2',
                                             'btu_per_fahHrFt2',
                                             'btu_per_rankSecFt2',
                                             'btu_per_fahSecFt2',
                                             'w_per_cm2kel']                                       

    switch (item) {
        case 'Power':
            return {
                component: 'agSelectCellEditor',
                params: {values: power_units},
            }

        case 'thermalResistance':
            return {
                component: 'agSelectCellEditor',
                params: {values: thermal_resistance_units},
            }

        case 'ThermalResistance':
            return {
                component: 'agSelectCellEditor',
                params: {values: thermal_resistance_units},
            }

        case 'SpecificHeat':
            return {
                component: 'agSelectCellEditor',
                params: {values: specific_heat_units},
            }

        case 'Temperature':
            return {
                component: 'agSelectCellEditor',
                params: {values: temperature_units},
            }

        case 'Thickness':
            return {
                component: 'agSelectCellEditor',
                params: {values: thickness_units},
            }

        case 'Mass':
            return {
                component: 'agSelectCellEditor',
                params: {values: mass_units},
            }

        case 'mass_flow':
            return {
                component: 'agSelectCellEditor',
                params: {values: mass_flow_units},
            }

        case 'heatTransferCoefficient':
            return {
                component: 'agSelectCellEditor',
                params: {values: heat_transfer_coefficient_units},
            }

    }

    return 'agTextCellEditor'
};


// Set which rows can have editable units column 
function editUnitsBox(value) {
    switch(value) {
        case 'Power':
            return true;

        case 'thermalResistance':
            return true;

        case 'ThermalResistance':
            return true;

        case 'SpecificHeat':
            return true;

        case 'Mass Flow':
            return true;

        case 'Temperature':
            return true;
            
        case 'Thickness':
            return true;

        case 'Mass':
            return true;

        case 'mass_flow':
            return true;

        case 'heatTransferCoefficient':
            return true;

        default:
            return false;
    }
};