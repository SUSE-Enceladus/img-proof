.PHONY: docs

deploy-docs: docs
	if [ -d "/tmp/ipa-docs/" ]; then rm -Rf /tmp/ipa-docs/; fi
	cp -r docs/build/html/. /tmp/ipa-docs/
	git checkout gh-pages
	find . -maxdepth 1 -not -name '.git' -exec rm -rv {} \;
	cp -r /tmp/ipa-docs/. .
	git add -A
	git commit -m "Publishing updated Sphinx docs to Github Pages."
	git push origin gh-pages

docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

module-docs:
	rm -rf docs/source/modules/
	SPHINX_APIDOC_OPTIONS='members,special-members,private-members,undoc-members,show-inheritance' sphinx-apidoc -P -e -o docs/source/modules/ ipa

