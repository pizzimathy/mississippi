
setup:
	mkdir map_shapefiles
	mkdir maps
	pip install -r requirements.txt
	echo "This package requires Python 3.6.5 or better."

clean:
	rm map_shapefiles/*
	rm maps/*