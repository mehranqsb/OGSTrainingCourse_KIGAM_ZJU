<?xml version="1.0" encoding="utf-8"?>
<OpenGeoSysGLI>
    <name>double_fracture</name>
    <points>
        <point id="0" x="0.1" y="0" z="0"/>
        <point id="1" x="0.1" y="1" z="0"/>
        <point id="2" x="12.6" y="1" z="0"/>
        <point id="3" x="12.6" y="0" z="0"/>
        <point id="4" x="0.1" y="0.3" z="0"/>
        <point id="5" x="0.1" y="0.301" z="0"/>
        <point id="6" x="12.6" y="0.3"  z="0"/>
        <point id="7" x="12.6" y="0.301" z="0"/>
        <point id="8" x="0.1" y="0.7" z="0"/>
        <point id="9" x="0.1" y="0.701" z="0"/>
        <point id="10" x="12.6" y="0.7"  z="0"/>
        <point id="11" x="12.6" y="0.701" z="0"/>        
    </points>
    <polylines>
        <polyline id="0" name="Left">
            <pnt>0</pnt>
            <pnt>1</pnt>
        </polyline>
        <polyline id="1" name="Top">
            <pnt>1</pnt>
            <pnt>2</pnt>
        </polyline>
        <polyline id="2" name="Right">
            <pnt>2</pnt>
            <pnt>3</pnt>
        </polyline>
        <polyline id="3" name="Bot">
            <pnt>3</pnt>
            <pnt>0</pnt>
        </polyline>
        <polyline id="4" name="Frac0_in">
            <pnt>4</pnt>
            <pnt>5</pnt>
        </polyline>
        <polyline id="5" name="Frac0_out">
            <pnt>6</pnt>
            <pnt>7</pnt>
        </polyline>
        <polyline id="6" name="Frac1_in">
            <pnt>8</pnt>
            <pnt>9</pnt>
        </polyline>
        <polyline id="7" name="Frac1_out">
            <pnt>10</pnt>
            <pnt>11</pnt>
        </polyline>        
    </polylines>
</OpenGeoSysGLI>
