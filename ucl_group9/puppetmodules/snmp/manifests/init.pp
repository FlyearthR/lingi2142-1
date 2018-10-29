# Include module 'snmp' to puppet in 'site.pp'
# Put this file in puppetmodules/snmp/manifests
class snmp (
  Array $trap_functions,
  String $sysLocation = "Undefined",
  String $sysContact = "Group 9 <arthur.sluyters@student.uclouvain.be>",
  Boolean $is_monitor = "false"
) {

  # Get the name of the node
  $node_name = lookup("name")

  # Create directory with correct permissions
  file {"/etc/snmp":
    ensure => directory,
    owner => root,
    group => root,
  }

  # Fill the template file and place the result in "/etc/snmp/snmpd.conf"
  file {"/etc/snmp/snmpd.conf":
    require => File["/etc/snmp"],
    ensure => file,
    content => template("/templates/snmpd.conf.erb"),
    owner => root,
    group => root,
  }

  # Start snmpd when the templates are created
  exec {"snmpd":
    require => File["/etc/snmp/snmpd.conf"],
    command => "snmpd",
  }

  # Setup trap notifiers
  file {"/etc/scripts":
    ensure => directory,
    owner => root,
    group => root,
  }

  file {"/etc/scripts/trapnotifier.conf":
    require => File["/etc/scripts"],
    ensure => file,
    content => template("/templates/trapnotifier.conf.erb"),
    owner => root,
    group => root,
  }

  # Start monitoring
  if $is_monitor {
    file {"/etc/scripts/agent_list.conf":
      require => File["/etc/scripts"],
      ensure => file,
      source => "/templates/agent_list.conf",
      owner => root,
      group => root,
    }
    file {"/etc/monitoring":
      ensure => directory,
      owner => root,
      group => root,
    }
  }
}


