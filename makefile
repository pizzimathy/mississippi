
setup:
	echo "Creating necessary directories."
	mkdir map_shapefiles
	mkdir maps
	echo "Installing requirements."
	pip install -r requirements.txt
	git clone https://github.com/apizzimenti/spanning_trees.git
	echo "This package requires Python 3.6.5 or better."

clean:
	rm map_shapefiles/*
	rm maps/*