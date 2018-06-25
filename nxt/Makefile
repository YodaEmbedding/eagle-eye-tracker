.PHONY: clean download run

clean:
	rm nxt.rxe

nxt.rxe nxt.nxc:
	nbc -EF nxt.nxc

download:
	nbc -EF -S=usb -d nxt.nxc

run:
	nbc -EF -S=usb -d -r nxt.nxc

