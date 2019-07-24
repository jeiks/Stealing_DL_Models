SOURCE = source/compute_heatmaps.cpp
TARGET = source/lrp_demo

CXX_FLAGS = -I../../include/   \
			-I../../build/src/ \
			-I/usr/include/hdf5/serial  \
			-I/usr/include/ImageMagick-6 \
			-I/usr/include/x86_64-linux-gnu/ImageMagick-6/ \
			-I/usr/include/opencv/  \
			-L/usr/lib/x86_64-linux-gnu/ \
			-Wl,--whole-archive \
			../../build/lib/libcaffe.a  \
			-Wl,--no-whole-archive \
			-lpthread -lglog -lgflags -lprotobuf -lleveldb \
			-lsnappy -lboost_system -lhdf5_serial_hl -lhdf5_serial \
			-llmdb -lopencv_core -lopencv_highgui -lopencv_imgproc \
			-latlas -lcblas \
			-lMagick++-6.Q16 -lMagickWand-6.Q16 -lMagickCore-6.Q16 \
			-lboost_filesystem -lboost_system -lboost_thread  -lpthread \
			-DCPU_ONLY

build:
	@test -d ../../demonstrator || { \
		echo Firstly, you have to dowload LRP Toolbox from;\
		echo https://github.com/sebastian-lapuschkin/lrp_toolbox/tree/master/caffe-master-lrp;\
		echo Then, you have to build it and copy this folder to \"caffe-master-lrp/demonstrator\";\
		echo Finally, you can use this code and run \"make build\" again.;\
		echo ;\
		exit 1;\
	}
	g++ $(SOURCE) -o $(TARGET) $(CXX_FLAGS)

clean:
	rm -f $(TARGET)

run:
	@echo 'Steps:'
	@echo "./run_lrp.sh PROBLEM_FOLDER"
	@echo "./gen_maps.sh PROBLEM_FOLDER"
	@echo "./join3.sh img1 img2 img3 output-prefix"
