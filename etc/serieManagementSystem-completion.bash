_seriesManagementSystem()
{
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="--make-new-exercise --build-serie --build-all-series --make-workbook --make-catalogue --preview-exercise --preview-solution"
    optssimple="-e -s -u -k -t"
    exercices=`ls Exercices/ |awk -F "ex" '{print $2}'| sort -g`
    
    case "${prev}" in
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
	   #local addopts=`ls Exercices/ |awk -F "ex" '{print $2}'| sort -g`
           #local addopts=$(for x in `ls Exercices/ |awk -F "ex" '{print $2}'| sed -e 's/\^\[\[0m\$//g'| sort -g`; do echo ${x}; done)
           #local addopts=`ls -l Exercices/ |grep ex | awk -F "ex" '{print $2}'|sort -g`
           local addopts=`ls Exercices/ |awk -F "ex" '{print $2}'| sed -e 's/\^\[\[0m\$//g'| sort -g | sed -r 's/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g' `
           #echo $addopts
           #local addopts=$(for x in `ls Exercices/ |sed -e 's/ex//g'| sort -g| tr -d [:alpha:]`; do echo ${x}; done)
           #local addopts=$(for x in `ls Exercices/ | tr -d [:alpha:]`; do echo ${x}; done)
           COMPREPLY=( $(compgen -W "${addopts}" -- ${cur}) ) 
           return 0
           ;;
    esac
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
    
}
complete -F _seriesManagementSystem seriesManagementSystem
