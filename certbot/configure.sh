#!/bin/bash

CURRENT_DIR=$(cd $(dirname $0); pwd)

echo "Let's Encrypt证书申请和续签一键脚本"

# main domain
while read -ep $'请输入申请证书的主域名（如 google.com, google.com.hk）\n' -a domain
do
    if [[ -z "${domain}" ]]; then
        echo "主域名不能为空！"
        continue
    fi
    break
done

# subdomain list
while read -ep $'请输入申请证书的子域名，多个用空格分隔（如 blog.google.com, *.google.com.hk）\n' -a subdomains
do
    if [[ -z "${subdomains}" ]]; then
        echo "子域名不能为空！"
        continue
    fi

    for subdomain in ${subdomains[@]}
    do
       result=$(echo "${subdomain}" | grep "${domain}")
        if [[ "${result}" == "" ]]; then
            break
        fi
    done
    if [[ "${result}" == "" ]]; then
        echo "子域名必须从属于主域名！"
        continue
    fi

    break
done

# domain provider
echo "请选择域名解析服务商"
echo '1: 腾讯云（DNSPod）'
echo '2: 自定义'
read provider_id

provider_name=''
case $provider_id in
    1)
        provider_name='txy'
        ;;
    *)
        if [[ -z "$provider_name" ]]; then
            read -ep $'请输入自定义域名解析服务商名称，并确保 `provider` 目录下有同名驱动程序\n' provider_name
        fi
esac

while read -ep $'请输入域名解析服务商提供的API Secret ID\n' secret_id
do
    if [[ -z "${secret_id}" ]]; then
        echo "API Secret ID 不能为空！"
        continue
    fi
    break
done

while read -ep $'请输入域名解析服务商提供的API Secret Key\n' secret_key
do
    if [[ -z "${secret_key}" ]]; then
        echo "API Secret Key 不能为空！"
        continue
    fi
    break
done

echo "主域名：${domain}"
echo "子域名列表：${subdomains[@]}"
echo "域名服务商：${provider_name}"
echo "Secret ID：${secret_id}"
echo "Secret Key：${secret_key}"

# generate script files
domain_fileds=''
for subdomain in ${subdomains[@]}
do
    domain_fileds="${domain_fileds} -d ${subdomain}"
done
domain_fileds=$(echo ${domain_fileds} | sed -e 's/^ //g')

update_script_filename='deploy_update.sh'
update_script_file="${CURRENT_DIR}/${update_script_filename}"
update_script_content=$(cat <<- EOF
if [[ -f "${update_script_file}" ]]; then
    echo "检测到部署更新脚本，执行脚本（${update_script_file}）。"
    ${update_script_file} ${domain}
fi
EOF
)

auth_hook="${CURRENT_DIR}/hook.sh add ${provider_name} ${secret_id} ${secret_key} ${domain}"
cleanup_hook="${CURRENT_DIR}/hook.sh clear ${provider_name} ${secret_id} ${secret_key} ${domain}"

apply_scrip_filename='certbot_apply.sh'
echo "certbot certonly ${domain_fileds} --manual --preferred-challenges dns --dry-run --manual-auth-hook '${auth_hook}' --manual-cleanup-hook '${cleanup_hook}'" > ${apply_scrip_filename}
echo "${update_script_content}" >> ${apply_scrip_filename}
chmod 755 ${apply_scrip_filename}
echo "已生成申请脚本（${apply_scrip_filename}）。"

renew_script_filename='certbot_renew.sh'
echo "certbot renew --manual --preferred-challenges dns --dry-run --manual-auth-hook '${auth_hook}' --manual-cleanup-hook '${cleanup_hook}'" > ${renew_script_filename}
echo "${update_script_content}" >> ${renew_script_filename}
chmod 755 ${renew_script_filename}
echo "已生成续签脚本（${renew_script_filename}）。"

echo "如在申请证书后，需要部署证书并更新重启Web服务器等，请在当前目录提供 ${update_script_filename} 以供调用执行。"
