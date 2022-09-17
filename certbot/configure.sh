#!/bin/bash

CURRENT_DIR=$(cd $(dirname $0); pwd)

echo "Let's Encrypt证书申请和续签一键脚本"

# main domain
while read -ep $'请输入申请证书的主域名（如 metazion.com）\n' -a domain
do
    if [[ -z "${domain}" ]]; then
        echo "主域名不能为空！"
        continue
    fi
    break
done

# complete domain
while read -ep $'请输入申请证书的完整域名，多个用空格分隔（如 metazion.com, *.metazion.com）\n' -a complete_domains
do
    if [[ -z "${complete_domains}" ]]; then
        echo "完整域名不能为空！"
        continue
    fi

    for complete_domain in ${complete_domains[@]}
    do
       result=$(echo "${complete_domain}" | grep "${domain}")
        if [[ "${result}" == "" ]]; then
            break
        fi
    done
    if [[ "${result}" == "" ]]; then
        echo "完整域名必须从属于主域名！"
        continue
    fi

    break
done

# email address
while read -ep $'请输入接收通知的电子邮箱（如 foo.gmail.com）\n' -a email
do
    if [[ -z "${email}" ]]; then
        echo "电子邮箱不能为空！"
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
echo "完整域名列表：${complete_domains[@]}"
echo "域名服务商：${provider_name}"
echo "Secret ID：${secret_id}"
echo "Secret Key：${secret_key}"

# generate script files
domain_fileds=''
for complete_domain in ${complete_domains[@]}
do
    domain_fileds="${domain_fileds} -d ${complete_domain}"
done
domain_fileds=$(echo ${domain_fileds} | sed -e 's/^ //g')

hook_dns_file="${CURRENT_DIR}/hook_dns.sh"
auth_hook="${hook_dns_file} add ${provider_name} ${secret_id} ${secret_key} ${domain}"
cleanup_hook="${hook_dns_file} clear ${provider_name} ${secret_id} ${secret_key} ${domain}"

hook_deploy_file="${CURRENT_DIR}/hook_deploy.sh"
deploy_hook="${hook_deploy_file} ${domain}"

apply_scrip_filename='certbot_apply.sh'
echo "certbot certonly ${domain_fileds} -m ${email} --manual --preferred-challenges dns --manual-auth-hook '${auth_hook}' --manual-cleanup-hook '${cleanup_hook}'" > ${apply_scrip_filename}
chmod 755 ${apply_scrip_filename}
echo "已生成申请脚本（${apply_scrip_filename}）。"

renew_script_filename='certbot_renew.sh'
echo "certbot renew -m ${email} --manual --preferred-challenges dns --manual-auth-hook '${auth_hook}' --manual-cleanup-hook '${cleanup_hook}' --deploy-hook '${deploy_hook}'" > ${renew_script_filename}
chmod 755 ${renew_script_filename}
echo "已生成续签脚本（${renew_script_filename}）。"

echo "如需续签证书后，部署证书并重启Web服务器等，请在 ${hook_deploy_file} 提供相关功能。"
