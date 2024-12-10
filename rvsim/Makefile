subdirs := sample

.PHONY: all clean $(subdirs)

all: $(subdirs)

$(subdirs):
	$(MAKE) -C $@

clean:
	$(RM) -rf *.o *.so *~ *.log __pycache__
	for dir in $(subdirs) ; do  $(MAKE) -C $$dir clean ; done
