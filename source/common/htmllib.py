
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

button_back = '''
  <a href="/..">
    <button class="button_base button_control">Back</button>
  </a>
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







