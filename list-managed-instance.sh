#!/bin/bash

ec2_instances=$(aws ec2 describe-instances --query "Reservations[*].Instances[*].[InstanceId,State.Name,Tags,Platform,PlatformDetails]" --output json --profile sts)

ssm_instances=$(aws ssm describe-instance-information --query "InstanceInformationList[*].[InstanceId]" --output json --profile sts)

if ! command -v jq &> /dev/null
then
    echo "jq가 설치되어 있지 않습니다. 설치 후 다시 시도하세요."
    exit
fi

total_instances=0
managed_by_ssm=0
not_managed_by_ssm=0
running_instances=0
stopped_instances=0
terminated_instances=0

for instance in $(echo "${ec2_instances}" | jq -r '.[][]| @base64'); do
    _jq() {
        echo ${instance} | base64 --decode | jq -r ${1}
    }
    instance_id=$(_jq '.[0]')
    state=$(_jq '.[1]')
    tags=$(_jq '.[2]')
    platform=$(_jq '.[3]')
    platform_details=$(_jq '.[4]')
    name=$(echo "${tags}" | jq -r '.[]? | select(.Key == "Name") | .Value // "N/A"')

    if [ -n "${platform}" ]&& [ "${platform}" != "null" ]; then
        os_type="${platform}"
    elif [ -n "${platform_details}" ]&& [ "${platform_details}" != "null" ]; then
        os_type="${platform_details}"
    else
        os_type="Linux/UNIX"
    fi

    total_instances=$((total_instances + 1))

    if [ "${state}" == "running" ]; then
        running_instances=$((running_instances + 1))
    elif [ "${state}" == "stopped" ] || [ "${state}" == "stopping" ] || [ "${state}" == "pending" ]; then
        stopped_instances=$((stopped_instances + 1))
    elif [ "${state}" == "terminated" ]; then
        terminated_instances=$((terminated_instances + 1))
    fi

    if echo "${ssm_instances}" | jq -e ".[][]| select(. == \"${instance_id}\")" > /dev/null; then
        if [ "${state}" == "running" ]; then
            ssm_status="Managed by SSM"
            managed_by_ssm=$((managed_by_ssm + 1))
        else
            ssm_status=""
        fi
    else
        if [ "${state}" == "running" ]; then
            ssm_status="Not Managed"
            not_managed_by_ssm=$((not_managed_by_ssm + 1))
        else
            ssm_status=""
        fi
    fi

    printf "%-20s %-54s %-13s %-10s %-s\n" "${instance_id}" "${name}" "${os_type}" "${state}" "${ssm_status}"
done

total_instances=$((total_instances - terminated_instances))
not_managed_by_ssm=$((running_instances - managed_by_ssm))

printf "Total Instances      : %3d\n" "${total_instances}"
printf "Running Instances    : %3d\n" "${running_instances}"
printf "Stopped Instances    : %3d\n" "${stopped_instances}"
printf "Managed by SSM       : %3d\n" "${managed_by_ssm}"
printf "Not Managed          : %3d\n" "${not_managed_by_ssm}"
if [ "${terminated_instances}" -ge 1 ]; then
    printf "Terminated Instances : %3d\n" "${terminated_instances}"
fi
echo -e "---------------------------------"
echo -e "${total_instances}\t${running_instances}\t${stopped_instances}\t${managed_by_ssm}\t${not_managed_by_ssm}"
echo -e ""
