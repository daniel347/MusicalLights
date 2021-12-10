button_styling = """
background-color: darkcyan;
font-family: Helvetica;
text-align: center;
border-radius: {};
"""

nav_bar_button_styling = """
background:none;
border:none;
margin:0;
padding:0;
"""

colour_display_styling = """
background-color: rgba({}, {}, {}, 1);
color: {};
font-family: Helvetica;
font-size: 14pt;
"""

slider_styling = """
QSlider::groove:horizontal {
    border: 0px solid;
    height: 16px;
    margin: 0px;
    border-radius: 8px;
    background-color: darkgrey;
}
QSlider::handle:horizontal {    
    background-color: darkcyan;
    border: 0px solid;
    height: 16px;
    width: 40px;
    border-radius: 8px;
    margin: 0px 0px;
}"""

colour_sequence_styling = """
QFrame#{} {{
    border: {} solid;
    border-color: black; 
    margin: 0pt;
    padding: 0pt;
    border-radius: 5px;
}}
"""