.PHONY: docs

docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

module-docs:
	rm -rf docs/source/modules/
	SPHINX_APIDOC_OPTIONS='members,special-members,private-members,undoc-members,show-inheritance' sphinx-apidoc -P -e -o docs/source/modules/ img_proof

