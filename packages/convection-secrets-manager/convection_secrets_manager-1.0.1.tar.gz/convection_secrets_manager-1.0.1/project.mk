
PROJECT_OWNER := AccidentallyTheCable
PROJECT_EMAIL := cableninja@cableninja.net
PROJECT_FIRST_YEAR := 2023
PROJECT_LICENSE := GPLv3
PROJECT_NAME := convection-secrets-manager
PROJECT_DESCRIPTION := Convection Secrets Manager
PROJECT_VERSION := 1.0.0

## Enable Feature 'Python'
BUILD_PYTHON := 1
## Enable Feature 'Shell'
BUILD_SHELL := 0
## Enable Feature 'Docker'
BUILD_DOCKER := 0
## Enable python `dist` Phase for Projects destined for PYPI
PYTHON_PYPI_PROJECT := 1
## Additional Flags for pylint. EX --ignore-paths=mypath
PYLINT_EXTRA_FLAGS := 

### Any Further Project-specific make targets can go here
project_lint:  ## Project-specific lint actions
	pip install -e .

spec_update:  ## Update Generated files
	generate-spec-docs -p ${THIS_DIR}/src/convection.secrets/server/specs/ -o ${THIS_DIR}/CONFIG.md.tmp
	sed -r 's/(Auto generated from .spec files)\n?$$/\1\n\n---TOPBLOCK---\n/g' CONFIG.md.tmp > CONFIG.md.tmp1
	mv CONFIG.md.tmp1 CONFIG.md.tmp
	sed -r 's/^(## Spec for secrets-controller)/---SNIP---\n\1/g' CONFIG.md.tmp | sed -r 's/(## Spec for secrets-controller)\n?$$/---END SNIP---\n\1/g' > CONFIG.md.tmp1
	mv CONFIG.md.tmp1 CONFIG.md.tmp
	sed -rz 's/(.*|\n)---TOPBLOCK---\n(.*|\n)---SNIP---\n(.*|\n)\n---END SNIP---\n(.*|\n)/\1\3\2\4/g' CONFIG.md.tmp > CONFIG.md.tmp1
	mv CONFIG.md.tmp1 CONFIG.md.tmp
	sed -r 's/Spec for secrets-controller/Top Level/g' CONFIG.md.tmp > CONFIG.md.tmp1
	mv CONFIG.md.tmp1 CONFIG.md.tmp
	echo "## Config Example\n\n\`\`\`toml\n" > /tmp/part.tmp
	cat /tmp/part.tmp ${THIS_DIR}/example-config.toml CONFIG.md.tmp > CONFIG.md
	rm CONFIG.md.tmp /tmp/part.tmp
