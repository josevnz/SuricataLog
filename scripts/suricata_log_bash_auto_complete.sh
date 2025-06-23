#!/usr/bin/env bash
:<<DOC
SuricataLog Bash completion (double tab key) for the following scripts:

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

    _default_suricata_eve_log_file="/var/log/suricata/eve.json"
    _default_suricata_eve_log_timestamp="$(eve_bash_auto_complete --timestamp)"

    _eve_bash_auto_complete() {
      if [[ "${#COMP_WORDS[@]}" == "2" ]]; then
        local words="--install --remove --timestamp --help"
        local current_word="${COMP_WORDS[$COMP_CWORD]}"
        mapfile -t COMPREPLY< <(compgen -W "$words" -- "$current_word")
        return 0
      fi
      COMPREPLY=()
    } && complete -F _eve_bash_auto_complete eve_bash_auto_complete

    _eve_json() {
      local current_word="${COMP_WORDS[$COMP_CWORD]}"
      local previous_word="${COMP_WORDS[$COMP_CWORD - 1]}"
      words="--timestamp --nxdomain --payload --flow --netflow --useragent --help"

      mapfile -t COMPREPLY< <(compgen -W "$words" -- "$current_word")
      return 0
    } && complete -o filenames -F _eve_json eve_json

    _eve_log() {
      local current_word="${COMP_WORDS[$COMP_CWORD]}"
      local previous_word="${COMP_WORDS[$COMP_CWORD - 1]}"
      if [[ "${#COMP_WORDS[@]}" -eq 2 ]]; then
        case "$current_word" in
          -*)
            words="--timestamp --help"
            mapfile -t COMPREPLY< <(compgen -W "$words" -- "$current_word")
            ;;
        esac
      elif [[ "${#COMP_WORDS[@]}" -eq 4 ]]; then
        case "$previous_word" in
          --timestamp)
            local completions
            # Timestamps have spaces, prevent them from being broken
            local old_ifs=$IFS
            IFS="*"
            completions="$(eve_bash_auto_complete --timestamp)"
            mapfile -t COMPREPLY < <(compgen -W "$completions" -- "$current_word")
            IFS=$old_ifs
            ;;
        esac
      elif [[ "${#COMP_WORDS[@]}" -gt 4 ]]; then
        local eve_files
        eve_files=$(compgen -f /var/log/suricata/eve*.json)
        if [[ -n $eve_files ]]; then
          mapfile -t COMPREPLY < <(compgen -W "$eve_files" -- "$current_word")
        fi
      fi
      return 0
    } && complete -o filenames -F _eve_log eve_log

    _eve_server() {
      local current_word="${COMP_WORDS[$COMP_CWORD]}"
      local previous_word="${COMP_WORDS[$COMP_CWORD - 1]}"

      if [[ ${COMP_CWORD} -eq 1 ]]; then
        mapfile -t COMPREPLY < <(compgen -W "--application --port" -- "$current_word")
        return 0
      fi
      # Previous word is --application
      if [[ "$previous_word" == "--application" ]]; then
        local applications="eve_log eve_json"
        mapfile -t COMPREPLY< <(compgen -W "$applications" -- "$current_word")
        return 0
      fi
      # Check if the previous word is --port
      if [[ "$previous_word" == "--port" ]]; then
        local ports="8000 8080 8001"
        mapfile -t COMPREPLY< <(compgen -W "$ports" -- "$current_word")
        return 0
      fi
      # Check if the previous word is the application name
      if [[ "$previous_word" == "eve_log" || "$previous_word" == "eve_json" || "$previous_word" =~ ^[0-9]+$ ]]; then
        mapfile -t COMPREPLY< <(compgen -f /var/log/suricata/*.json -- "$current_word")
        return 0
      fi
      COMPREPLY=()
    } && complete -o filenames -F _eve_server eve_server

    _eve_payload() {
      local current_word="${COMP_WORDS[$COMP_CWORD]}"
      local previous_word="${COMP_WORDS[$COMP_CWORD - 1]}"
      # Current word is the first argument
      if [[ ${COMP_CWORD} -eq 1 ]]; then
        mapfile -t COMPREPLY< <(compgen -W "--report_dir" -- "$current_word")
        return 0
      fi
      # Previous word is --report_dir
      if [[ "$previous_word" == "--report_dir" ]]; then
        mapfile -t COMPREPLY< <(compgen -d -- "$current_word")
        return 0
      fi
      # Previous word is the report directory
      if [[ -d "$previous_word" ]]; then
        mapfile -t COMPREPLY< <(compgen -f /var/log/suricata/*.json -- "$current_word")
        return 0
      fi
      COMPREPLY=()
    } && complete -F _eve_payload eve_payload

  fi
else
  printf "ERROR: Missing requirements.\nBash version: '%s'.\nVirtual environment='%s'.\n" "${BASH_VERSION:-MISSING}" "${VIRTUAL_ENV:-MISSING}"
fi