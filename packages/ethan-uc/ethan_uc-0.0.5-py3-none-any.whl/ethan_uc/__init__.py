construction = "not done yet"
missing_unit = "Unit is either missing or nonexistent. Some units are not supported."
overflow_error = "Overflow Error"
avaliable_temp_units = ["c", "f", "k", "r", "de"]
avaliable_angle_units = ["deg", "rad", "sign", "grad"]
__version__ = "0.0.5"

# Convert Temperatures
def temp(raw_temp, unit1="f", unit2="c", ):
    try:
        temp = int(raw_temp)
    except ValueError:
        return "NaN"
    try:
        if unit1 == "c":  # From Celsius to other units
            if unit2 == "c":
                return temp
            elif unit2 == "f":
                return ((9 / 5) * temp) + 32
            elif unit2 == "k":
                return temp + 273.15
            elif unit2 == "r":
                return temp * (9 / 5) + 491.67
            elif unit2 == "de":
                return (100 - temp) * (3 / 2)
            else:
                return missing_unit
        elif unit1 == "f":  # From Fahrenheit to other units
            if unit2 == "c":
                return (5 / 9) * (temp - 32)
            elif unit2 == "f":
                return temp
            elif unit2 == "k":
                return (temp - 32) * (5 / 9) + 273.15
            elif unit2 == "r":
                return temp + 459.67
            elif unit2 == "de":
                return (212 - temp) * (5 / 6)
            else:
                return missing_unit
        elif unit1 == "k":  # From Kelvin to other units
            if unit2 == "c":
                return temp - 273.15
            elif unit2 == "f":
                return temp * (9 / 5) - 459.67
            elif unit2 == "k":
                return temp
            elif unit2 == "r":
                return temp * (9 / 5)
            elif unit2 == "de":
                return (373.15 - temp) * (3 / 2)
            else:
                return missing_unit
        elif unit1 == "r":  # From Rankine to other units
            if unit2 == "c":
                return (temp - 491.67) * (5 / 9)
            elif unit2 == "f":
                return temp - 491.67
            elif unit2 == "k":
                return temp * (5 / 9)
            elif unit2 == "r":
                return temp
            elif unit2 == "de":
                return (671.67 - temp) * (5 / 6)
            else:
                return missing_unit
        elif unit1 == "de":  # From Delisle to other units
            if unit2 == "c":
                return 100 - temp * (2 / 3)
            elif unit2 == "f":
                return 212 - temp * (6 / 5)
            elif unit2 == "k":
                return 373.15 - temp * (2 / 3)
            elif unit2 == "r":
                return 671.67 - temp * (6 / 5)
            elif unit2 == "de":
                return temp
            else:
                return missing_unit
        else:
            return missing_unit
    except OverflowError:
        return overflow_error

# Convert angles
def angle(raw_angle, unit1="deg", unit2="rad"):
    try: # Ensure it is an interger
        angle = int(raw_angle) 
    except ValueError:
        return "NaN" 
    
    try:
        if unit1 == "deg": # From degrees
            if unit2 == "deg":
                return angle
            elif unit2 == "rad":
                return angle/57.296
            elif unit2 == "sign":
                return angle*0.033333
            elif unit2 == "grad":
                return angle*1.1111
            else:
                return missing_unit
        elif unit1 == "rad": # From radians
            if unit2 == "deg":
                return angle*57.296
            elif unit2 == "rad":
                return angle
            elif unit2 == "sign":
                return angle*1.9099
            elif unit2 == "grad":
                return angle * 63.662
            else:
                return missing_unit
        elif unit1 == "sign": # From sign
            if unit2 == "deg":
                return angle*30
            elif unit2 == "rad":
                return angle/1.9099
            elif unit2 == "sign":
                return angle
            elif unit2 == "grad":
                return angle*33.333
            else:
                return missing_unit    
        elif unit1 == "grad": # From gradians
            if unit2 == "deg":
                return angle*0.9
            elif unit2 == "rad":
                return angle/63.662
            elif unit2 == "sign":
                return angle*0.03
            elif unit2 == "grad":
                return angle
            else:
                return missing_unit    
        else:
            return missing_unit
    except OverflowError:
        return overflow_error
    
        
    