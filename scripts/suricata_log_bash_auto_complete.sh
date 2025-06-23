#!/usr/bin/env bash
:<<DOC
SuricataLog Bash completion (double tab key) for the following scripts:

  - eve_json
  - eve_log
  - eve_server
  - eve_payload
  - eve_bash_auto_complete

To enable auto-completion, this file will be copied to the following location:
- $HOME/.local/share/bash-completion/completions

Bash auto completion is a complicated subject:
  - https://www.gnu.org/software/bash/manual/html_node/A-Programmable-Completion-Example.html#A-Programmable-Completion-Example

Note than I only generate auto completion for the most common flags. User can figure out the rest by calling '--help'.

DOC
if [[ -n $BASH_VERSION && -n $VIRTUAL_ENV ]]; then
  if (return 0 2>/dev/null); then

    _default_suricata_eve_log_file="/var/log/suricata/eve.json"
    _default_suricata_eve_log_timestamp="$(eve_bash_auto_complete --timestamp)"

    _eve_bash_auto_complete() {
      local current_word="${COMP_WORDS[$COMP_CWORD]}"
      local previous_word="${COMP_WORDS[$COMP_CWORD - 1]}"
      if [[ ${COMP_CWORD} -eq 1 ]]; then
        local words="--install --remove --timestamp --help"
        mapfile -t COMPREPLY< <(compgen -W "$words" -- "$current_word")
        return 0
      fi
      COMPREPLY=()
    } && complete -F _eve_bash_auto_complete eve_bash_auto_complete

    _eve_json() {
      local current_word="${COMP_WORDS[$COMP_CWORD]}"
      local previous_word="${COMP_WORDS[$COMP_CWORD - 1]}"
      local options="--help --timestamp --nxdomain --payload --flow --netflow --useragent"
      local json_files=(/var/log/suricata/*.json)
      # First argument
      if [[ ${COMP_CWORD} -eq 1 ]]; then
        if [[ "${#json_files[@]}" -gt 0 ]]; then
          mapfile -t COMPREPLY< <(compgen -W "$options ${json_files[*]}" -- "$current_word")
        else
          mapfile -t COMPREPLY< <(compgen -W "$options" -- "$current_word")
        fi
        return 0
      fi
      # Previous word is an option
      case "$previous_word" in
        "--timestamp")
          local completions
          completions=$(eve_bash_auto_complete --timestamp)
          completions="${completions//[[:space:]]/\\ }"
          mapfile -t COMPREPLY < <(compgen -W "$completions" -- "$current_word")
          return 0
          ;;
        "--netflow")
          mapfile -t COMPREPLY< <(compgen -W "127.0.0.1" -- "$current_word")
          return 0
          ;;
        "--help" | "--nxdomain" | "--payload" | "--flow" | "--useragent")
          return 0
          ;;
      esac
      # All options have been provided
      if [[ "${#COMP_WORDS[@]}" -gt $((COMP_CWORD + 1)) ]]; then
        mapfile -t COMPREPLY< <(compgen -f /var/log/suricata/*.json -- "$current_word")
        return 0
      fi
      COMPREPLY=()
    } && complete -o filenames -F _eve_json eve_json

    _eve_log() {
      local current_word="${COMP_WORDS[$COMP_CWORD]}"
      local previous_word="${COMP_WORDS[$COMP_CWORD - 1]}"
      local options="--help --timestamp"
      local json_files=(/var/log/suricata/*.json)
      # First argument
      if [[ ${COMP_CWORD} -eq 1 ]]; then
        if [[ "${#json_files[@]}" -gt 0 ]]; then
          mapfile -t COMPREPLY< <(compgen -W "$options ${json_files[*]}" -- "$current_word")
        else
          mapfile -t COMPREPLY< <(compgen -W "$options" -- "$current_word")
        fi
        return 0
      fi
      # Previous word is an option
      if [[ "$previous_word" == "--timestamp" ]]; then
        local completions
        completions=$(eve_bash_auto_complete --timestamp)
        completions="${completions//[[:space:]]/\\ }"
        mapfile -t COMPREPLY < <(compgen -W "$completions" -- "$current_word")
        return 0
      elif [[ "$previous_word" == "--help" ]]; then
        return 0
      fi
      # All options have been provided
      if [[ "${#COMP_WORDS[@]}" -gt $((COMP_CWORD + 1)) ]]; then
        mafile -t COMPREPLY< <(compgen -f /var/log/suricata/*.json -- "$current_word")
        return 0
      fi
      COMPREPLY=()
    } && complete -o filenames -F _eve_log eve_log

    _eve_server() {
      local current_word="${COMP_WORDS[$COMP_CWORD]}"
      local previous_word="${COMP_WORDS[$COMP_CWORD - 1]}"
      # First time
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
      # Previous word is --port
      if [[ "$previous_word" == "--port" ]]; then
        local ports="8000 8080 8001"
        mapfile -t COMPREPLY< <(compgen -W "$ports" -- "$current_word")
        return 0
      fi
      # Previous word is the application name or the port number
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