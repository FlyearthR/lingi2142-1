# Puppet looks in data/node.yaml for radvd::RADVD, radvd::prefix, radvd::route, radvd::interface automatically
# These variables are now accessible in the template
class bind (Boolean $RADVD = false, String $prefix, String $route, String $interface) {
  # Get name of the node (lookup in data/node.yaml
  $node_name = lookup("name")
  if $RADVD {
    file {"/etc/radvd.conf":
      ensure => directory,
      source => template("/templates/radvd.conf.erb"),
      recurse => true,
    }
    file {"/etc/init.d":
      ensure => directory,
      recurse => true,
    }
    file {"/etc/init.d/radvd":
      require => File["/etc/init.d"],
      ensure => file,
      source => template("/templates/init.d/radvd"),
    }
    exec { "radvd":
      require => File["/etc/radvd.conf"],
      require => File["/etc/init.d/radvd"],
      command => "radvd -C /etc/radvd.conf",
    }
  }

}
