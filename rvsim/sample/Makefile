subdirs := life squash fact

.PHONY: all clean $(subdirs)

all: $(subdirs)

$(subdirs):
	$(MAKE) -C $@

clean:
	$(RM) *~
	for dir in $(subdirs) ; do  $(MAKE) -C $$dir clean ; done
