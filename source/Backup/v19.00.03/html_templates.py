
head = '''
<title>INNOVA Tools Test</title>
<head>
  <style type="text/css">
    table,th,td{{
      border:1px solid black;
      border-collapse: collapse;
      text-align: left;
      vertical-align: top;
    }}   
    th, td{{
      padding-right:20;
      padding-right:20;
      padding-top: 6px;
      padding-bottom: 6px;

    }}
    a {{
      text-decoration:none;
    }}
    .button_base {{
      background-color: #4CAF50; /* Green */
      border: none;
      color: white;
      padding: 15px 32px;
      text-align: center;
      text-decoration: none;
      display: inline-block;
      font-size: 16px;
      margin: 4px 2px;
      cursor: pointer;
    }}
    .button_lang {{background-color: #008CBA;}} /* Blue */
    .button_control {{background-color: #555555;}} /* Black*/ 
    .button_util {{background-color: #008CBA;}} /* Blue */ 
    .button_input_submit {{background-color: #4CAF50; color: white; padding: 5px 15px;}} /* Gray */ 
    .button_download {{background-color: #555555;}} /* Black */
 
    .inputtext{{
      width:70%;
      padding: 5px 15px;
    }}

  
    body {{
      margin: 20px 50px;
    }}
    form {{ display: inline; }}
    
    .fixtop {{
     position: fixed; /* Set the navbar to fixed position */
    }}
  </style>
</head>
'''


button_prefresh = '''
 <button class="button_base" value="Refresh Page" onClick="window.location.reload();">{}</button>
'''

button = '''
 <a href="{href}">
  <button class="{style}">{display}</button>
 </a>
'''

submit_button = '''
<form action="" method="post">
  <input class="{style}" type="submit" name="submit_button" value="{val}">
</form>
'''

input_form = '''
<form action="" method="post">
  <input type="text" style="width:50%; padding: 5px 15px;" placeholder="{placeholder}" name="{name}" value="{input_val}">
  <input class="button_base button_input_submit" type="submit" name="submit_button" value="{btn_val}"">
</form>
'''

download_vin_button = '''
<form action="" method="post">
  <button class="" type="submit" name="submit_button" value="{val}">Download</button>
</form>
'''




dtc_convert_page = head + '''
<body>
  <a href="/..">
    <button class="button_base button_control">Back</button>
  </a>

  <br><br>

  <form action="" method="post">
    <input type="text" style="width:50%; padding: 5px 15px;" placeholder="Enter DTC" name="dtc-input" value="{dtc_input}">
    <input class="button_base button_input_submit" type="submit" name="submit_button" value="Convert To Hex">
  </form>

  <form action="" method="post">
    <input type="text" style="width:50%; padding: 5px 15px;" placeholder="Enter Hex Number" name="hex-input" value="{hex_input}">
    <input class="button_base button_input_submit" type="submit" name="submit_button" value="Convert To DTC">
  </form>
</body>
'''





create_obdii_sim_page = head + '''
<body>
  <a href="/..">
    <button class="button_base button_control">Back</button>
  </a>

  <br>
  <br>
  <p style="color:Red;">{result}</p>

  <form action="" method="post">
    <b style="font-size:20px;">Mode $09</b><br>
    <input type="text" class="inputtext" placeholder="Input filename" name="filename" value=""><br><br><br>

    <b style="font-size:20px;">Protocol Selection</b><br><br>
    <input type="radio" style="margin-left: 30px;" name="protocol" value="CAN" checked> Protocol CAN  
    <input type="radio" style="margin-left: 30px;" name="protocol" value="PWM"> Protocol PWM
    <input type="radio" style="margin-left: 30px;" name="protocol" value="ISO9141"> Protocol ISO9141
    <input type="radio" style="margin-left: 30px;" name="protocol" value="KW2000"> Protocol KW2000
    <br><br><br>

    <b style="font-size:20px;">Mode $09</b><br>
    <input type="text" class="inputtext" placeholder="Input VIN (Default: FFFFFFFFFFFFFFFF)" name="vin-input" value=""><br><br><br>

    <b style="font-size:20px;">Mode $03</b><br>
    <input type="text" class="inputtext" placeholder="Input mode $03 DTCs (Example: P0001, P1001, P2001, P3001)" name="dtc03s-input" value=""><br><br><br>

    <b style="font-size:20px;">Mode $07</b><br>
    <input type="text" class="inputtext" placeholder="Input mode $0A DTCs (Example: P0001, P1001, P2001, P3001)" name="dtc07s-input" value=""><br><br><br>

    <b style="font-size:20px;">Mode $0A</b><br>
    <input type="text" class="inputtext" placeholder="Input mode $0A DTCs (Example: P0001, P1001, P2001, P3001)" name="dtc0As-input" value=""><br><br><br>
    
    <input type="submit" class="button_base button_input_submit"  name="submit_button" value="Submit">
  </form>
</body>
'''



