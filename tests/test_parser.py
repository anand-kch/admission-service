import hl7

def test_hl7_parsing():
    # Use a raw string (r'') to prevent backslash issues
    # HL7 segments are separated by \r (carriage return)
    raw_hl7 = r'MSH|^~\&|LAB|HOSPITAL|ADT|1|20260509||ADT^A01|123|P|2.3' + '\r' + \
              r'PID|1||10000^^^MRN||DOE^JOHN||19800101|M'
    
    h = hl7.parse(raw_hl7)
    pid_seg = h.segment('PID')
    
    # Accessing PID-3 (Patient Identifier List)
    # [3] = Field 3
    # [0] = First repetition
    patient_id_field = pid_seg[3][0]
    
    # In some versions of the library/message, we need to check length 
    # before accessing component index 4 (MRN)
    patient_id = str(patient_id_field[0])
    
    try:
        id_type = str(patient_id_field[4])
    except IndexError:
        # If the parser didn't split components, the whole string might be in [0]
        # This fallback helps debug exactly what the parser sees
        print(f"Warning: Could not find component at index 4. Full field: {patient_id_field}")
        id_type = "UNKNOWN"

    print(f"\n--- Testing HL7 Parsing ---")
    print(f"Extracted ID: {patient_id}")
    print(f"Extracted Type: {id_type}")
    
    assert "10000" in patient_id
    print("Test Passed!")

if __name__ == "__main__":
    test_hl7_parsing()