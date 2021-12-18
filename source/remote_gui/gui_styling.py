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

mode_selection_styling = """
QComboBox {
    border: 1px solid gray;
    border-radius: 30px;
    padding: 5px 40px 5px 20px;
    min-width: 6em;
    height: 60px;
}

QComboBox::down-arrow {
    image: url("./remote_gui/DropdownArrow.png");
    background-color: darkcyan;
    border: 0px;
    transform: rotate(90deg);
    
    height: 40px;
    width: 40px;
    border-radius: 20px;
    
    margin: 0px 30px 0px 0px
}

QComboBox::down-arrow:on {
    transform: rotate(-90deg);
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    
    border-radius: 25px
}

QComboBox QAbstractItemView {
    border: 2px solid darkgray;
    border-radius: 20px;
    selection-background-color: darkcyan;
}
"""
