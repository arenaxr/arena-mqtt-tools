arena_sub.py: venv
	$(VENV)/python $@ $(ARGS)

gen-root-jwt.py: venv
	$(VENV)/python $@ $(ARGS)

mqtt-tester.py: venv
	$(VENV)/python $@ $(ARGS)

signout: venv
			$(VENV)/python -c 'from arena import auth ; auth.signout()'

show-req: venv
		$(VENV)/pip freeze

freeze: venv
				$(VENV)/pip freeze | sed s/=.*// > requirements.txt

include Makefile.venv
Makefile.venv:
	curl \
		-o Makefile.fetched \
		-L "https://github.com/sio/Makefile.venv/raw/v2020.08.14/Makefile.venv"
	echo "5afbcf51a82f629cd65ff23185acde90ebe4dec889ef80bbdc12562fbd0b2611 *Makefile.fetched" \
		| shasum -a 256 --check - \
		&& mv Makefile.fetched Makefile.venv
