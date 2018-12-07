# Puppet looks in data/node.yaml for bind::bind automatically
class bind (Boolean $bind = false) {
  # We only configure bing if we are on nameserver
  if $bind {
    file {"/etc/bind":
      ensure => directory,
      source => 'puppet:///bind',
      recurse => remote,
      owner => root,
      group => root,
    }
    file {"/etc/init.d":
      ensure => directory,
      owner => root,
      group => root,
      recurse => true,
    }
    file {"/etc/init.d/bind9":
      require => File["/etc/init.d"],
      ensure => file,
      owner => root,
      group => root,
      mode => '777',
      source => template("/templates/init.d/bind9"),
    }
    exec { "bind":
      require => [File["/etc/bind"], File["/etc/init.d/bind9"]],
      command => "/etc/init.d/bind9 start",
    }
  }
  #But every host need to know what are the adresses of the nameserver
  file {"/etc/resolv.conf":
    ensure => file,
    content => template("/templates/resolv.conf"),
  }
}
