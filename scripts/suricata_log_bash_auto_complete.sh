#!/usr/bin/env bash
:<<DOC
SuricataLog Bash completion for the following scripts:

  - eve_json
  - eve_log
  - eve_server
  - eve_payload
  - eve_bash_auto_complete

To enable auto-completion, this file should be copied to the following location:
- $HOME/.local/share/bash-completion/completions

More details at: https://github.com/scop/bash-completion/blob/main/README.md

DOC
if [[ -n $BASH_VERSION && -n $VIRTUAL_ENV ]]; then
  if (return 0 2>/dev/null); then

    _eve_bash_auto_complete() {
      local words="--install --remove --help"
      if [ "${#COMP_WORDS[@]}" != "2" ]; then
        return
      fi
      mapfile -t COMPREPLY< <(compgen -W "$words" -- "${COMP_WORDS[1]}")
      return 0
    }
    complete -F _eve_bash_auto_complete eve_bash_auto_complete

    _eve_json() {
      local latest="${COMP_WORDS[$COMP_CWORD]}"
      local prev="${COMP_WORDS[$COMP_CWORD - 1]}"
      words=""

      mapfile -t COMPREPLY< <(compgen -W "$words" -- "$latest")
      return 0
    }
    complete -F _eve_json eve_json

    _eve_log() {
      local latest="${COMP_WORDS[$COMP_CWORD]}"
      local prev="${COMP_WORDS[$COMP_CWORD - 1]}"
      local words=""

      mapfile -t COMPREPLY< <(compgen -W "$words" -- "$latest")
      return 0
    }
    complete -F _eve_log eve_log

    _eve_server() {
      local latest="${COMP_WORDS[$COMP_CWORD]}"
      local prev="${COMP_WORDS[$COMP_CWORD - 1]}"
      local words="--application --port --help"
      case "${prev}" in
          --application)
            words="eve_log eve_json"
            ;;
          --port)
            words="8000 8080 8001"
            ;;
          --help)
            ;;
          *)
            ;;
        esac
      mapfile -t COMPREPLY< <(compgen -W "$words" -- "$latest")
      return 0
    }
    complete -F _eve_server eve_server

    _eve_payload() {
      local latest="${COMP_WORDS[$COMP_CWORD]}"
      local prev="${COMP_WORDS[$COMP_CWORD - 1]}"
      local words=""

      mapfile -t COMPREPLY< <(compgen -W "$words" -- "$latest")
      return 0
    }
    complete -F _eve_payload eve_payload

  else
    echo "ERROR: Please install to '$HOME/.local/share/bash-completion/completions/suricata_log_bash_auto_complete.sh'"
  fi
else
  printf "ERROR: Missing requirements.\nBash version: '%s'.\nVirtual environment='%s'.\n" "${BASH_VERSION:-MISSING}" "${VIRTUAL_ENV:-MISSING}"
fi