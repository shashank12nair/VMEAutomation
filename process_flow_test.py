import datetime

from base_functions import *
import time

boardtype = vme.BoardType["V1718"] #communication bridge board name
linknumber = "0"
conetnode = 0

#Code to get fixed number of qdc output data. Change max_count to required number of events.
#output will be a .csv file





with vme.Device.open(boardtype, linknumber, conetnode) as device:
    demo = InteractiveDemo(device)

    demo.set_vme_baseaddress("B990000") #base address of QDC module
    time.sleep(0.1)
    demo.set_address_modifier("A24_U_DATA")
    time.sleep(0.1)
    # demo.set_data_width("D32")
    # time.sleep(0.5)

    # Output CSV path
    timestamp = datetime.datetime.now().strftime("%Y%m%d%_H%M%S")
    csv_filename = "vme_data_output_" + timestamp + ".csv"
    valid_data_count = 0
    max_count = 10
    output_data = []

    print("Starting data acquisition...")
    # Save collected data to CSV


    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Data"])

    demo.set_data_width("D16")
    time.sleep(0.1)
    demo.write_cycle("1032", "4") #clearing the data by writing to the "bit set 2 register"
    time.sleep(0.5)
    demo.write_cycle("1034", "4") #disabling the "bit set 2" enabled bit by writing to the "bit clear 2" register
    time.sleep(0.5)
    demo.write_cycle("1040", "0") #clearing the event counter register


    while valid_data_count <max_count:
        # Step 1: Read the status register
        demo.set_data_width("D16")
        time.sleep(0.1)
        status_word = demo.read_cycle("1022")
        if status_word is None:
            continue

        # Step 2: Check bit 0 (data available)
        if not status_word & 0x2:
            # Read from output buffer at address 0x0000

            demo.set_data_width("D32")
            time.sleep(0.1)
            data_word = demo.read_cycle("0000")
            if data_word is None:
                continue

            # Check if bits 24–26 are 0
            if (data_word >> 24) & 0x7 == 0:
                output_data.append(data_word)
                valid_data_count += 1
                print(f"[{valid_data_count}] Data accepted: {data_word:08X}")
                time.sleep(0.1)
                with open(csv_filename, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    for i, val in enumerate(output_data):
                        writer.writerow([i + 1, f"{val:08X}"])



            else:
                print("Data rejected due to bits 24-26")

        # Optional: Sleep briefly to avoid CPU hogging
        time.sleep(1)

    demo.set_data_width("D32")
    time.sleep(0.1)
    data_word = demo.read_cycle("0000")

    if(data_word >> 24) & 0x7 == 4:
        counter = data_word & 0xFFFFFF


    print(f"Data acquisition complete. {valid_data_count} entries saved to {csv_filename}, counter value {int(counter) + 1}")#counter counts from 0







