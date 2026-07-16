Name:           ripgrep
Version:        15.2.0
Release:        1%{?dist}
Summary:        ripgrep recursively searches directories for a regex pattern while respecting your gitignore

URL:            https://github.com/BurntSushi/ripgrep
License:        MIT AND Unlicense
Source0:        https://github.com/BurntSushi/ripgrep/archive/refs/tags/%{version}.tar.gz

BuildRequires:  git
BuildRequires:  python3
BuildRequires:  curl
BuildRequires:  gcc

%define debug_package %{nil}
%global bin_name rg

# Amazon Linux 2023 rust-lld workaround
%if 0%{?amzn} == 2023
%undefine _package_note_flags
%global al2023_rustflags -C link-arg=-fuse-ld=bfd
%endif

%description
ripgrep is a line-oriented search tool that recursively searches the
current directory for a regex pattern.

By default, ripgrep will respect gitignore rules and automatically skip
hidden files/directories and binary files.

ripgrep is similar to other popular search tools like The Silver
Searcher, ack and grep.

%package bash-completion
Summary: Bash completion files for %{name}
Requires: bash-completion
Requires: %{name} = %{version}-%{release}
BuildArch: noarch

%description bash-completion
%{summary}

%post -n ripgrep-bash-completion
if [ ! -L /etc/bash_completion.d/%{bin_name} ]; then
    ln -s %{_datadir}/bash-completion/completions/%{bin_name} \
        /etc/bash_completion.d/%{bin_name}
fi

if [ -f /etc/bash_completion.d/%{bin_name}.bash ]; then
    rm -f /etc/bash_completion.d/%{bin_name}.bash
fi

%postun -n ripgrep-bash-completion
if [ "$1" -eq 0 ]; then
    rm -f /etc/bash_completion.d/%{bin_name}
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

%if 0%{?amzn} == 2023
mkdir -p .cargo

cat > .cargo/config.toml << 'EOF'
[target.x86_64-unknown-linux-gnu]
linker = "gcc"

[target.aarch64-unknown-linux-gnu]
linker = "gcc"
EOF

export RUSTFLAGS="%{al2023_rustflags}"
%endif

curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

export PATH="$PATH:$HOME/.cargo/bin"

cargo build \
    --release \
    --features 'pcre2'

target/release/%{bin_name} --generate man \
    > %{bin_name}.1

target/release/%{bin_name} --generate complete-bash \
    > bash_complete_%{bin_name}

target/release/%{bin_name} --generate complete-zsh \
    > zsh_complete_%{bin_name}

target/release/%{bin_name} --generate complete-fish \
    > fish_complete_%{bin_name}

gzip -9 %{bin_name}.1

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_mandir}/man1
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions
mkdir -p %{buildroot}%{_datadir}/fish/vendor_completions.d
mkdir -p %{buildroot}%{_datadir}/zsh/site-functions

install -m 0755 \
    target/release/%{bin_name} \
    %{buildroot}%{_bindir}/%{bin_name}

install -m 0644 \
    %{bin_name}.1.gz \
    %{buildroot}%{_mandir}/man1/%{bin_name}.1.gz

install -m 0644 \
    bash_complete_%{bin_name} \
    %{buildroot}%{_datadir}/bash-completion/completions/%{bin_name}

install -m 0644 \
    zsh_complete_%{bin_name} \
    %{buildroot}%{_datadir}/zsh/site-functions/_%{bin_name}

install -m 0644 \
    fish_complete_%{bin_name} \
    %{buildroot}%{_datadir}/fish/vendor_completions.d/%{bin_name}.fish

%check
export PATH="$PATH:$HOME/.cargo/bin"

%if 0%{?amzn} == 2023
export RUSTFLAGS="%{al2023_rustflags}"
%endif

cargo test --release --locked --all

%files
%license LICENSE-MIT UNLICENSE COPYING
%doc README.md CHANGELOG.md

%{_bindir}/%{bin_name}
%{_mandir}/man1/%{bin_name}.1.gz

%files bash-completion
%{_datadir}/bash-completion/completions/%{bin_name}

%files fish-completion
%{_datadir}/fish/vendor_completions.d/%{bin_name}.fish

%files zsh-completion
%{_datadir}/zsh/site-functions/_%{bin_name}

%changelog
* Thu Jul 16 2026 - Danie de Jager - 15.2.0-1
* Sun May 10 2026 - Danie de Jager - 15.1.0-3
* Fri Jan 23 2026 - Danie de Jager - 15.1.0-2
* Wed Oct 22 2025 - Danie de Jager - 15.1.0-1
* Mon Oct 20 2025 - Danie de Jager - 15.0.0-1
* Fri Aug 15 2025 - Danie de Jager - 14.1.1-5
- Updated license
* Mon Jun 16 2025 - Danie de Jager - 14.1.1-5
* Mon Feb 17 2025 - Danie de Jager - 14.1.1-4
* Tue Dec 17 2024 - Danie de Jager - 14.1.1-3

* Mon Sep 16 2024 - Danie de Jager - 14.1.1-2
- Add man and autocompletion scripts.

* Mon Sep 16 2024 - Danie de Jager - 14.1.1-1
- Initial version
