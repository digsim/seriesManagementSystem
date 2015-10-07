_seriesManagementSystem()
{
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="--make-new-exercise --build-serie --build-all-series --make-workbook --make-catalogue --preview-exercise --preview-solution --make-new-lecture"
    optssimple="-e -s -u -k -t -l"

    
    case "${prev}" in
        --make-new-lecture)
            local addopts="-l"
            COMPREPLY=( $(compgen -W "${addopts}" -- ${cur}) )
            return 0
            ;;
        --build-serie)
            local addopts="-s"
            COMPREPLY=( $(compgen -W "${addopts}" -- ${cur}) ) 
            return 0
            ;;
        --preview-exercise)
            local addopts="-e"
            COMPREPLY=( $(compgen -W "${addopts}" -- ${cur}) ) 
            return 0
            ;;
       --preview-solution)
            local addopts="-e"
            COMPREPLY=( $(compgen -W "${addopts}" -- ${cur}) ) 
            return 0
            ;;
       -s)
           local addopts=$(for x in `ls Series_properties/ |awk -F "serie|.cfg" '{print $2}'|sort -g`; do echo ${x}; done)
           COMPREPLY=( $(compgen -W "${addopts}" -- ${cur}) ) 
           return 0
           ;;
       -e)
           local addopts=`ls Exercices/ |awk -F "ex" '{print $2}'| sed 's:/$::' |sort -g`
           COMPREPLY=( $(compgen -W "${addopts}" -- ${cur}) ) 
           return 0
           ;;
    esac
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
    
}
complete -F _seriesManagementSystem seriesManagementSystem
