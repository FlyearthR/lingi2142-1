# Puppet looks in data/node.yaml for bird6::routing_id and bird6::ospfv3 automatically
# These variables are now accessible in the template
class bird6 (
  String $routing_id,
  Hash $ospfv3,
  Boolean $bgp = false,
  Integer $asn = 0,
  Integer $gnum = 0
) {
  # Get name of the node (lookup in data/node.yaml
  $node_name = lookup("name")
  $peerasn = 200
  $peernum = 1
  
  # Create directory with correct permissions
  file {"/etc/bird":
    ensure => directory,
    owner  => bird,
    group  => bird,
  }
  # Fill the template file and place the result in "/etc/bird/bird6.conf"
  file {"/etc/bird/bird6.conf":
    require => File["/etc/bird"],
    ensure => file,
    content => template("/templates/bird6.conf.erb"),
    owner  => bird,
    group  => bird,
  }

  # Start bird6 when the template is created
  exec { "bird6-launch":
    require => File["/etc/bird/bird6.conf"], # Force to execute the command after
    command => "bird6 -s /tmp/${node_name}_bird6.ctl",
  }
  $dev = $asn ? {
    200 => "b",
    default => "a",
  }
  if $bgp {
    exec { "adding-routes":
      command => "ip route add dev belnet${dev} \"fd00:${asn}:${gnum}::/48\"; ip address add dev belnet${dev} \"fd00:${asn}::${gnum}/48\"",
    }
  }
}
