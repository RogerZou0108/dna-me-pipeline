#!/usr/bin/env python2.7
# tool_versions.py v1.1  Creates "SW" versions json string for a particular DX applet.
#                        Write request to stdout and verbose info to stderr.  This allows easy use in dx app scripts.

import sys, os, argparse, json, commands

# APP_TOOLS is a dict keyed by applet script name with a list of tools that it uses.
APP_TOOLS = {
    # dna-me:    
    "dme-map-pe":           [ "mott-trim-pe.py", "bismark", "bowtie2", "samtools" ],
    "dme-map-se":           [ "mott-trim-se.py", "bismark", "bowtie2", "samtools" ],
    "dme-merge-bams":       [ "bismark", "bowtie2", "samtools" ],
    "dme-extract-pe":       [ "bismark_methylation_extractor", "samtools" ],
    "dme-extract-se":       [ "bismark_methylation_extractor", "samtools" ],

    # utility:    
    "dme-index-bismark":    [ "bismark_genome_preparation", "bowtie2" ],
    }
# Virtual apps only differ from their parent by name/version. 
VIRTUAL_APPS = {
    # lrna virtuals:    
    "dme-merge-bams-alt":   "dme-merge-bams",
    }


# ALL_TOOLS contains the printable tool name (key) and the command that is used to determine the version.
ALL_TOOLS = {
            "bismark":                      "bismark --version | grep Version | awk '{print $3}'",
            "bismark_genome_preparation":   "bismark_genome_preparation --version | grep Version | awk '{print $5}'",
            "bismark_methylation_extractor":"bismark_methylation_extractor --version | grep Version | awk '{print $4}'",
            "bismark2bedGraph":             "bismark2bedGraph --version | grep Version | awk '{print $4}'",
            "bismark2report":               "bismark2report --version | grep version | awk '{print $3}'",
            "coverage2cytosine":            "coverage2cytosine --version | grep Version | awk '{print $4}'",
            "deduplicate_bismark":          "deduplicate_bismark --help | grep modified | awk '{printf \"%s %s %s %s %s %s\n\",$4,$5,$6,$7,$8,$9}'",
            "samtools":                     "samtools 2>&1 | grep Version | awk '{print $2}'",
            "bowtie2":                      "bowtie2 --version 2>&1 | grep bowtie | awk '{print $3}'",
            "bowtie2-build":                "bowtie2-build --version 2>&1 | grep bowtie | awk '{print $3}'",
            "bowtie2-inspect":              "bowtie2-inspect --version 2>&1 | grep bowtie | awk '{print $3}'",
            "mott-trim-pe.py":              "echo unversioned",
            "mott-trim-se.py":              "echo unversioned",
            "bedToBigBed":                  "bedToBigBed 2>&1 | grep 'bedToBigBed v' | awk '{print $2$3}'",

            #"bedGraphToBigWig":          "bedGraphToBigWig 2>&1 | grep 'bedGraphToBigWig v' | awk '{print $2$3}'",
            }

def parse_dxjson(dxjson):
    '''Parses the dnanexus-executable.json file in the job directory to get applet name and version.'''
    with open(dxjson) as data_file:    
        dxapp = json.load(data_file)

    appver = "unknown"    
    applet = dxapp.get("name")
    if "version" in dxapp:
        appver = dxapp.get("version")
    else:
        title = dxapp.get("title")
        last_word = title.split(' ')[-1]
        if last_word.startswith('(virtual-') and last_word.endswith(')'):
            appver = last_word[9:-1]
        elif last_word.startswith('(v') and last_word.endswith(')'):
            appver = last_word[2:-1]
    
    return (applet, appver)


def main():
    parser = argparse.ArgumentParser(description =  "Versions parser for a dx applet. " + \
                                                    "Prints version lines to stderr and json string to stdout. " + \
                                                    "MUST specify either --applet and --appver or --dxjson.")
    parser.add_argument('-a','--applet', required=False,
                        help="Applet to print versions for")
    parser.add_argument('-av','--appver', required=False,
                        help="Version of applet")
    parser.add_argument('-j','--dxjson', required=False,
                        help="Use dnanexus json file to discover 'applet' and 'appver'")
    parser.add_argument('-q', '--quiet', action="store_true", required=False, default=False, 
                        help="Don't print versions to stderr.")
    parser.add_argument('-v', '--verbose', action="store_true", required=False, default=False, 
                        help="Show the command-line that is used to get the version.")


    args = parser.parse_args(sys.argv[1:])
    if len(sys.argv) < 3:
        parser.print_usage()
        return
        
    if (args.applet == None or args.appver == None) and args.dxjson == None:
        parser.print_help()
        return

    applet = args.applet
    applet = args.appver
    
    if args.dxjson != None:
        (applet,appver) = parse_dxjson(args.dxjson)
    
    versions = {}
    versions["DX applet"] = { applet: appver }
    if not args.quiet:
        sys.stderr.write("********\n")
        sys.stderr.write("* Running " + applet + ": " + appver+ "\n")
    
    if applet in VIRTUAL_APPS:
        tools = APP_TOOLS[VIRTUAL_APPS[applet]]
    else:
        tools = APP_TOOLS[applet]
    for tool in tools:
        cmd = ALL_TOOLS[tool]
        if args.verbose:
            sys.stderr.write("cmd> " + cmd + "\n")
        err, ver = commands.getstatusoutput(cmd)
        versions[tool] = ver
        if not args.quiet:
            sys.stderr.write("* " + tool + " version: " + ver + "\n")

    if not args.quiet:
        sys.stderr.write("********\n")
    
    print json.dumps(versions) 
     
if __name__ == '__main__':
    main()

