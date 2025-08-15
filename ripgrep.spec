Name:           ripgrep
Version:        14.1.1
Release:        6%{?dist}
Summary:        ripgrep recursively searches directories for a regex pattern while respecting your gitignore
URL:            https://github.com/BurntSushi/ripgrep
License:        MIT & Unlicense
Source0:        https://github.com/BurntSushi/ripgrep/archive/refs/tags/%{version}.tar.gz

BuildRequires:  git
BuildRequires:  python3
BuildRequires:  curl
BuildRequires:  gcc

%define debug_package %{nil}


%description
ripgrep is a line-oriented search tool that recursively searches the current directory for a regex pattern. By default, ripgrep will respect gitignore rules and automatically skip hidden files/directories and binary files. (To disable all automatic filtering by default, use rg -uuu.) ripgrep has first class support on Windows, macOS and Linux, with binary downloads available for every release. ripgrep is similar to other popular search tools like The Silver Searcher, ack and grep.

%package bash-completion
Summary: Bash completion files for %{name}
Requires: bash-completion
Requires: %{name} = %{version}-%{release}
BuildArch: noarch

%description bash-completion
%{summary}

%post -n ripgrep-bash-completion
if [ ! -L /etc/bash_completion.d/rg ]; then
    ln -s %{_datadir}/bash-completion/completions/rg /etc/bash_completion.d/rg
fi
if [ -f /etc/bash_completion.d/rg.bash ]; then
    rm -f /etc/bash_completion.d/rg.bash
fi

%postun -n ripgrep-bash-completion
if [ "$1" -eq 0 ]; then
    rm -f /etc/bash_completion.d/rg
fi

%package fish-completion
Summary: Fish completion files for %{name}
Requires: fish
Requires: %{name} = %{version}-%{release}
BuildArch: noarch

%description fish-completion
%{summary}

%package zsh-completion
Summary: ZSH completion files for %{name}
Requires: zsh
Requires: %{name} = %{version}-%{release}
BuildArch: noarch

%description zsh-completion
%{summary}


%prep
%setup -q

%build
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
export PATH="$PATH:$HOME/.cargo/bin"
$HOME/.cargo/bin/cargo build --release --features 'pcre2'
target/release/rg --generate man > rg.1
target/release/rg --generate complete-bash > bash_complete_rg || exit 1
target/release/rg --generate complete-zsh > zsh_complete_rg || exit 1
target/release/rg --generate complete-fish > fish_complete_rg || exit 1
gzip rg.1

%install
mkdir -p %{buildroot}/usr/share/bash-completion/completions
mkdir -p %{buildroot}/usr/share/fish/vendor_completions.d
mkdir -p %{buildroot}/usr/share/zsh/site-functions
mkdir -p %{buildroot}/usr/share/man/man1
install -D -m 755 target/release/rg %{buildroot}/usr/bin/rg
install -m 644 rg.1.gz %{buildroot}/usr/share/man/man1
install -m 644 bash_complete_rg %{buildroot}/usr/share/bash-completion/completions/rg
install -m 644 zsh_complete_rg %{buildroot}/usr/share/zsh/site-functions/_rg
install -m 644 fish_complete_rg %{buildroot}/usr/share/fish/vendor_completions.d/rg.fish

%check
$HOME/.cargo/bin/cargo test --release --locked --all

%files
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1.gz

%files bash-completion
%{_datadir}/bash-completion/completions/rg

%files fish-completion
%{_datadir}/fish/vendor_completions.d/rg.fish

%files zsh-completion
%{_datadir}/zsh/site-functions/_rg

%changelog
* Mon Jun 16 2025 - Danie de Jager - 14.1.1-5
* Mon Feb 17 2025 - Danie de Jager - 14.1.1-4
* Tue Dec 17 2024 - Danie de Jager - 14.1.1-3
* Mon Sep 16 2024 - Danie de Jager - 14.1.1-2
- Add man and autocompletion scripts.
* Mon Sep 16 2024 - Danie de Jager - 14.1.1-1
- Initial version
