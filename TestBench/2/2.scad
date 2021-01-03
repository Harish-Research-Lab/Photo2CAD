difference() {
	translate([0.0,0.0,0.0]){
	rotate([90,0,-45.0]){
		cube([2.0,1.0,2.0], center = true);
	}
}

	translate([-0.01,0,0.0]){
	rotate([90,0,0]){
		cylinder($fn = 12, h = 2.83, r1 = 0.26, r2 = 0.26, center = true);
	}
}
}
