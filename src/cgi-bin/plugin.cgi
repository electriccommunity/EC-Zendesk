#!/bin/sh

exec "$COMMANDER_HOME/bin/ec-perl" -x "$0" "${@}"

################################
#!perl
# plugin.cgi -
#
# Get/set the plugins configuration info for UI
#
# Copyright (c) 2007-2015 Electric Cloud, Inc.
# All rights reserved
################################

use strict;
use warnings;
use Getopt::Long;
use File::Spec;
use File::Temp;
use ElectricCommander;
use ElectricCommander::PropMod;
use ElectricCommander::PropDB;
use CGI qw(:standard);

use constant {
    SUCCESS => 0,
    ERROR   => 1,
};

# used for output redirection
$::tmpOut = "";
$::tmpErr = "";
$::oldout;
$::olderr;

################################
# main - Main program for the application.
#
# Arguments:
#   -
#
# Returns:
#   0 - Success
#   1 - Error
#
################################
sub main() {

    ## globals
    $::cg = CGI->new();
    $::opts = $::cg->Vars;
    $::ec = new ElectricCommander();
    $::ec->abortOnError(0);

    # make sure no libraries print to STDOUT
    saveOutErr();

    # Check for required arguments.
    if (!defined $::opts->{cmd} || "$::opts->{cmd}" eq "") {
        retError("error: cmd is required parameter");
    }

    # ---------------------------------------------------------------
    # Dispatch operation
    # ---------------------------------------------------------------
    for ($::opts->{cmd})
    {
        # modes
        /getCfgList/i and do   { getCfgList(); last; };
    }
    retError("unknown command $::opts->{cmd}");

    exit SUCCESS;
}


################################
# getCfgList - Return the list of configurations from the plugin
#
# Arguments:
#   -
#
# Returns:
#   0 - Success
#   1 - Error
#
################################
sub getCfgList {

    my $gcfg = new ElectricCommander::PropDB($::ec,"/projects/EC-Zendesk-1.3.0.135/plugin_cfgs");

    my %cfgs = $gcfg->getRows();
    # print results as XML block
    my $xml = "";
    $xml .= "<cfgs>\n";
    foreach my $cfg (keys  %cfgs) {
        $xml .= "  <cfg>\n";
        $xml .= "     <name>$cfg</name>\n";
        $xml .= "  </cfg>\n";
    }
    $xml .= "</cfgs>\n";
    
    printXML($xml);
    exit SUCCESS;
}

################################
# retError - Return an error message
#
# Arguments:
#   msg - Message to return
#
# Returns:
#   0 - Success
#   1 - Error
#
################################
sub retError {
    my ($msg) = @_;

    printXML("<error>$msg</error>\n");
    exit ERROR;
}

################################
# printXML - Print the XML block, add stdout, stderr
#
# Arguments:
#   xml - xml string to print
#
# Returns:
#   -
#
################################
sub printXML {
    my ($xml) = @_;

    my ($out,$err) = retrieveOutErr();
    print $::cg->header("text/html");
    print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
    print "<response>\n";
    print "$xml\n";
    print "<stdout>" . xmlQuote($out) . "</stdout>\n";
    print "<stderr>" . xmlQuote($err) . "</stderr>\n";
    print "</response>";
}

################################
# saveOutErr - Redirect stdout/stderr to files so that any spurious output from commands does not end up on the return to the cgi caller
#
# Arguments:
#   -
#
# Returns:
#   -
#
################################
sub saveOutErr {
    # temporarily save STDOUT/STDERR to files
    open $::oldout, ">&STDOUT"  or die "Can't dup STDOUT: $!";
    open $::olderr, ">&STDERR"  or die "Can't dup STDERR: $!";
    close STDOUT;
    open STDOUT, '>', \$::tmpOut or die "Can't open STDOUT: $!";
    close STDERR;
    open STDERR, '>', \$::tmpErr or die "Can't open STDOUT: $!";

}

################################
# retrieveOutErr - Reset stdout/sterr back to normal and return the contents of the temp files
#
# Arguments:
#   -
#
# Returns:
#   tmpOut - Content of out file
#   tmpErr - Content of error file
#
################################
sub retrieveOutErr {
    # reconnect to normal STDOUT/STDERR
    open STDOUT, ">&", $::oldout or die "can't reinstate $!";
    open STDERR, ">&", $::olderr or die "can't reinstate $!";
    return ($::tmpOut, $::tmpErr);
}

################################
# xmlQuote - Quote special characters such as & to generate well-formed XML character data.
#
# Arguments:
#   string - String whose contents should be quoted.
#
# Returns:
#   string - Quoted string
#
################################
sub xmlQuote($) {
    my ($string) = @_;

    $string =~ s/&/&amp;/g;
    $string =~ s/</&lt;/g;
    $string =~ s/>/&gt;/g;
    $string =~ s{([\0-\x{08}\x{0b}\x{0c}\x{0e}-\x{1f}])}{
    sprintf("%%%02x", ord($1))}ge;
    return $string;
}

main();
