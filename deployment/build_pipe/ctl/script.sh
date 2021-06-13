#! /bin/sh -xe

REPO=/dev/shm/build/SPMS
RENDER_ENV="BUILDER=${BUILDER} REGISTRY=${REGISTRY}"

# get source code
if [[ -d "${REPO}" ]]
then
	git -C "${REPO}" fetch
	git -C "${REPO}" reset --hard "origin/${BRANCH}"
else
	git clone gitolite:SPMS $REPO
fi
cd $REPO
git checkout "${BRANCH}"

cd deployment
eval "${RENDER_ENV}" python3 render.py

cd /dev/shm/build
make -f common_layers.makefile build
make -f pr.makefile build
make -f pv.makefile build
