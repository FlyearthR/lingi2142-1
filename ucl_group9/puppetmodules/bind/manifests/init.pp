# Puppet looks in data/node.yaml for bird6::routing_id and bird6::ospfv3 automatically
# These variables are now accessible in the template
class bind (Boolean $BIND = false) {
  # Get name of the node (lookup in data/node.yaml
  $node_name = lookup("name")
  if $BIND {
    file {"/etc/bind":
      ensure => directory,
      source => template("/templates/bind/"),
      recurse => true,
    }
    file {"/etc/init.d":
      ensure => directory,
      recurse => true,
    }
    file {"/etc/init.d/bind9":
      require => File["/etc/init.d"],
      ensure => file,
      source => template("/templates/puppetTmp/init.d/bind9"),
    }
    exec { "bind":
      require => File["/etc/bind"],
      require => File["/etc/init.d/bind9"],
      command => "/etc/init.d/bind9 start",
    }
  }

  file {"/etc/resolv.conf":
    ensure => file,
    source => template("/templates/resolv.conf",
  }

}
