# Puppet looks in data/node.yaml for radvd::radvd, radvd::prefix, radvd::route, radvd::interface automatically
# These variables are now accessible in the template
class radvd (Boolean $radvd = false, Hash $lans = {}) {
    
  if $radvd {
    file {"/etc/radvd.conf":
      ensure => file,
      owner => root,
      group => root,
      replace => true,
      content => template("/templates/radvd.conf.erb"),
    }
    file {"/etc/init.d":
      ensure => directory,
      owner => root,
      group => root,
      recurse => true,
    }
    file {"/etc/init.d/radvd":
      require => File["/etc/init.d"],
      ensure => file,
      owner => root,
      group => root,
      content => template("/templates/init.d/radvd"),
    }
    exec { "radvd":
      require => [File["/etc/radvd.conf"], File["/etc/init.d/radvd"]],
      command => "/etc/init.d/radvd start",
    }
  }

}
