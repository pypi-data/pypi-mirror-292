

ok so here's the rundown on all this stuff:

unpack_folder.py:
    - can unpack and relocate an entire folder of files compressed with fpack
    - deals with all the necessary renaming as well as deletes the compressed
     versions
    - usage: python unpack_folder.py infolderpath outfolderpath
    - if no outfolderpath is given, it will unpack them in infolder
    - paths can be with or without slash at the end

noise_info.py
    - analyzes background noise in chunks of arbitrary size(default=15 pixels)
    - returns a median/mean pixel value, matrix of each chunk's mean/median and a matrix of
     their standard deviations 
    - can make plot of means/medians vs stds, and 3d plot of each chunk's mean/median
    - has a rather extensive ui including multiple, gradually increasing in computational 
    overkill, methods of file searching for the lazy
    - will also automatically display when run in X window 
    Usage: python noise_info path/to/file 

fim.py
    - does everything noise_info can
    - everything you need to operate/change it is in default.cfg, just change the values and rerun
    - 

paths.py
    - stabilizes pathing accross accounts and machines
    - please add and use it as much as possible
    - but also dont change anything already there
    - gives you access to all path names pre-stored under variables

difference.py
    - this was a bid of a pipedream longshot from the start
    - just finds difference between fits files from SExtractor's perspective
    - good use of k-d tree if you wanna use the code for similar projects

flats_noise.py
    - i barely remember making this one
    - from when i was going insane trying to figure out how to denoise and renoise images
    - statistical nonsense


get_sources.py
    - SExtractor script, hardcoded to draw from my(Benny) own settings

    

gaussian.py
    - adds a pixel offset but radially symmetric, gaussian "star" at a randomized point around 
     a specific point(typically galaxies)
    - the offset adds surprisingly accurate radial irregularities
    - uniformly randomizes sigma of gaussian to be between siga and sigb
    - uniformly randomizes amp of gaussian
    - also randomizes placement around specified point (done in radial coordinate
     and transformed back to cartesian)
    - used by gym_teacher.py

gym_teacher.py
    - named gym teacher because it comes up with "games" to train the ai
    - takes in a folder of unpacked fits files and injects randomized new stars 
     into them around both the most galaxylike galaxies 
    - if there arent enough "galaxy-like" galaxies, it starts to pick random spots to fill its ranks
    - for each file it records name, star placements, star sigma, star amp, and star array size for
     each file in folder under starcoords.xml
